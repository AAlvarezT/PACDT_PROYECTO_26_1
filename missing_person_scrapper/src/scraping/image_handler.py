"""
Image handling module for missing persons data scraping
Handles screenshot capture and image processing using Selenium
"""

import time
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm
from typing import List, Optional
from .config import get_chrome_driver_options, PHOTO_XPATH


def initialize_chrome_driver():
    """
    Initialize Chrome WebDriver with the same options as original
    
    Returns:
        Chrome WebDriver instance
    """
    chrome_options = get_chrome_driver_options()
    return webdriver.Chrome(options=chrome_options)


def capture_image_screenshot(driver, page_url: str) -> Optional[np.ndarray]:
    """
    Capture screenshot of specific image on a webpage
    
    Args:
        driver: Selenium WebDriver instance
        page_url: URL of the webpage containing the image
    
    Returns:
        Image matrix as numpy array or None if capture fails
    """
    driver.get(page_url)
    try:
        time.sleep(1)  # Same delay as original
        
        # Wait for the image element (reproducing original logic)
        img_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, PHOTO_XPATH))
        )
        
        # Take screenshot of the specific image element
        screenshot_bytes = img_element.screenshot_as_png
        
        # Convert to OpenCV matrix (reproducing original conversion)
        img_pil = Image.open(BytesIO(screenshot_bytes))
        img_matrix = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        return img_matrix
        
    except Exception as e:
        print(f"Error al tomar el screenshot de la imagen en {page_url}: {e}")
        return None


def capture_images_from_link_list(case_links: List[str], description: str = "Processing links") -> List[np.ndarray]:
    """
    Capture images from a list of URLs with progress tracking
    
    Args:
        case_links: List of URLs to process
        description: Description for progress bar
    
    Returns:
        List of captured image matrices
    """
    # Initialize driver (reproducing original driver = iniciar_driver())
    driver = initialize_chrome_driver()
    captured_image_matrices = []
    
    try:
        # Process each link with progress bar (reproducing original tqdm loop)
        for case_link in tqdm(case_links, desc=description):
            image_matrix = capture_image_screenshot(driver, case_link)
            
            if image_matrix is not None:
                captured_image_matrices.append(image_matrix)
            else:
                # Log failed link for review (reproducing original error handling)
                print(f"Error procesando {case_link}")
        
    except Exception as e:
        print(f"Error during image capture: {e}")
        
    finally:
        # Close browser (reproducing original driver.quit())
        driver.quit()
    
    # Print summary (reproducing original print statement)
    print(f"Total de fotos capturadas: {len(captured_image_matrices)}")
    
    return captured_image_matrices


def capture_images_with_error_recovery(case_links: List[str], description: str = "Processing links") -> List[np.ndarray]:
    """
    Capture images from URLs with error recovery and driver restart
    
    Args:
        case_links: List of URLs to process
        description: Description for progress bar
    
    Returns:
        List of captured image matrices
    """
    driver = initialize_chrome_driver()
    captured_image_matrices = []
    
    for case_link in tqdm(case_links, desc=description):
        try:
            image_matrix = capture_image_screenshot(driver, case_link)
            if image_matrix is not None:
                captured_image_matrices.append(image_matrix)
                
        except Exception as e:
            print(f"Error al tomar el screenshot de la imagen en {case_link}: {e}")
            
            # Restart driver on error (reproducing original error recovery)
            try:
                driver.quit()
                driver = initialize_chrome_driver()
            except Exception as restart_error:
                print(f"Error restarting driver: {restart_error}")
                break
    
    # Close final driver instance
    try:
        driver.quit()
    except:
        pass
    
    print(f"Total de fotos capturadas: {len(captured_image_matrices)}")
    return captured_image_matrices


class ImageCaptureManager:
    """
    Context manager for handling image capture operations
    Provides clean resource management for WebDriver
    """
    
    def __init__(self):
        self.driver = None
    
    def __enter__(self):
        self.driver = initialize_chrome_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def capture_single_image(self, url: str) -> Optional[np.ndarray]:
        """Capture single image using managed driver"""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        return capture_image_screenshot(self.driver, url)
    
    def capture_multiple_images(self, urls: List[str], description: str = "Capturing images") -> List[np.ndarray]:
        """Capture multiple images using managed driver"""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        captured_images = []
        for url in tqdm(urls, desc=description):
            image_matrix = self.capture_single_image(url)
            if image_matrix is not None:
                captured_images.append(image_matrix)
            else:
                print(f"Failed to capture: {url}")
        
        return captured_images
