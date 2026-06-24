"""
topics.py
Topic modeling con clustering sobre texto libre (Circunstancias,
Vestimenta, Otras observaciones), usando TF-IDF + K-Means.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from utils import STOPWORDS_ES, log_step, logger, require_columns

# A diferencia de sentiment.py, aquí SÍ tiene sentido incluir
# 'Vestimenta': el clustering no depende de carga emocional, agrupa
# por similitud de palabras (p. ej. podría revelar patrones comunes de
# vestimenta), así que no hay razón para excluirla de antemano.
TOPIC_ELIGIBLE_COLUMNS = ["Circunstancias", "Vestimenta", "Otras observaciones"]

# TfidfVectorizer usa strip_accents="unicode" (quita tildes del texto
# ANTES de comparar contra stop_words), así que las stopwords también
# deben ir sin tilde o sklearn las deja pasar sin filtrar (se vio en
# pruebas: "más" no bloqueaba "mas" una vez quitado el acento).
_ACCENT_MAP = str.maketrans("áéíóúü", "aeiouu")
_STOPWORDS_ES_SIN_TILDE = list({w.translate(_ACCENT_MAP) for w in STOPWORDS_ES})


@log_step
def fit_topics(df: pd.DataFrame, col: str, n_topics: int = 4, top_terms: int = 8, random_state: int = 42) -> dict:
    """
    Ajusta TF-IDF + K-Means sobre los textos no vacíos de `col`.

    Parameters
    ----------
    df : DataFrame ya filtrado.
    col : columna de texto (ver TOPIC_ELIGIBLE_COLUMNS).
    n_topics : K, número de clusters/temas.
    top_terms : cuántos términos característicos mostrar por tema.
    random_state : semilla para reproducibilidad (K-Means y SVD).

    Returns
    -------
    dict con:
        - 'df': DataFrame original + columnas '{col}_tema' (int) y
          '{col}_tema_label' (str, ej. "Tema 2: domicilio, trabajo, hora").
        - 'terms_per_topic': {tema_id: [términos]}
        - 'labels': {tema_id: "Tema N: term1, term2, ..."}
        - 'sizes': {tema_id: n_casos}
        - 'silhouette': float | None
        - 'coords_2d': array (n_docs_con_texto, 2) para graficar
        - 'cluster_ids': array (n_docs_con_texto,)
        - 'mask': Series booleana de qué filas de df tenían texto

    Raises
    ------
    ValueError
        Si `col` no es elegible, no existe, hay menos documentos con
        texto que `n_topics`, o el vocabulario resultante queda vacío
        (textos muy cortos/repetitivos tras quitar stopwords).
    """
    require_columns(df, [col], context="fit_topics")
    if col not in TOPIC_ELIGIBLE_COLUMNS:
        raise ValueError(
            f"'{col}' no es una columna apta para topic modeling. "
            f"Columnas válidas: {TOPIC_ELIGIBLE_COLUMNS}"
        )

    df = df.copy()
    mask = df[col].notna() & (df[col].astype(str).str.strip() != "")
    textos = df.loc[mask, col].astype(str).tolist()

    if len(textos) < max(n_topics, 2):
        raise ValueError(
            f"Hay {len(textos)} casos con texto en '{col}', pero se pidieron {n_topics} temas. "
            "Reduce el número de temas o revisa los filtros aplicados."
        )

    try:
        vectorizer = TfidfVectorizer(
            stop_words=_STOPWORDS_ES_SIN_TILDE,
            max_df=0.6,
            min_df=2,
            lowercase=True,
            strip_accents="unicode",
        )
        X = vectorizer.fit_transform(textos)
    except ValueError as e:
        # Vocabulario vacío: textos muy cortos/repetitivos tras quitar
        # stopwords y aplicar min_df/max_df.
        raise ValueError(
            f"No se pudo construir vocabulario TF-IDF para '{col}' con los filtros "
            f"actuales (textos muy cortos o muy repetitivos): {e}"
        ) from e

    if X.shape[1] == 0:
        raise ValueError(f"El vocabulario TF-IDF para '{col}' quedó vacío con los filtros actuales.")

    kmeans = KMeans(n_clusters=n_topics, random_state=random_state, n_init=10)
    cluster_ids = kmeans.fit_predict(X)

    # Términos característicos por cluster: mayor peso TF-IDF PROMEDIO
    # dentro del cluster (no el centroide crudo de k-means), para que
    # refleje qué palabras realmente distinguen a ese grupo de casos.
    terms = np.array(vectorizer.get_feature_names_out())
    terms_per_topic = {}
    for k in range(n_topics):
        idx_cluster = np.where(cluster_ids == k)[0]
        if len(idx_cluster) == 0:
            terms_per_topic[k] = []
            continue
        mean_tfidf = np.asarray(X[idx_cluster].mean(axis=0)).ravel()
        top_idx = mean_tfidf.argsort()[::-1][:top_terms]
        terms_per_topic[k] = terms[top_idx].tolist()

    labels = {
        k: f"Tema {k + 1}: " + ", ".join(v[:5]) if v else f"Tema {k + 1}: (sin términos)"
        for k, v in terms_per_topic.items()
    }

    sizes = pd.Series(cluster_ids).value_counts().sort_index().to_dict()

    silhouette = None
    if n_topics > 1 and len(textos) > n_topics:
        try:
            silhouette = round(float(silhouette_score(X, cluster_ids)), 3)
        except Exception as e:
            logger.warning("No se pudo calcular silhouette score para '%s': %s", col, e)

    # TruncatedSVD (no PCA): opera sobre la matriz TF-IDF dispersa
    # directamente, sin densificarla -más eficiente en memoria para
    # vocabularios grandes-. Equivalente a LSA con 2 componentes.
    n_comp = min(2, X.shape[1] - 1) if X.shape[1] > 1 else 1
    coords_2d = TruncatedSVD(n_components=max(n_comp, 1), random_state=random_state).fit_transform(X)
    if coords_2d.shape[1] == 1:
        coords_2d = np.hstack([coords_2d, np.zeros((coords_2d.shape[0], 1))])

    score_col, label_col = f"{col}_tema", f"{col}_tema_label"
    df[score_col] = pd.NA
    df[label_col] = pd.NA
    df.loc[mask, score_col] = cluster_ids
    df.loc[mask, label_col] = [labels[k] for k in cluster_ids]

    return {
        "df": df,
        "terms_per_topic": terms_per_topic,
        "labels": labels,
        "sizes": sizes,
        "silhouette": silhouette,
        "coords_2d": coords_2d,
        "cluster_ids": cluster_ids,
        "mask": mask,
    }
