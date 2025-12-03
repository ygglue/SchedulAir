// Custom Carousel Implementation with Infinite Scroll
(function() {
  const carouselContainer = document.querySelector('.carousel-container');
  let carouselItems = document.querySelectorAll('.carousel-item');
  const prevBtn = document.querySelector('.carousel-btn-prev');
  const nextBtn = document.querySelector('.carousel-btn-next');
  const indicators = document.querySelectorAll('.carousel-indicators .indicator');
  const modal = document.getElementById('imageModal');
  const modalImage = document.getElementById('modalImage');
  const modalClose = document.querySelector('.modal-close');
  const modalPrev = document.querySelector('.modal-nav-prev');
  const modalNext = document.querySelector('.modal-nav-next');
  
  let currentIndex = 1; // Start at 1 because we'll clone items
  let currentModalIndex = 0;
  const totalItems = carouselItems.length;
  let isScrolling = false;

  // Clone items for infinite scroll
  function setupInfiniteScroll() {
    // Clone first item to end
    const firstClone = carouselItems[0].cloneNode(true);
    firstClone.setAttribute('data-clone', 'last');
    carouselContainer.appendChild(firstClone);
    
    // Clone last item to beginning
    const lastClone = carouselItems[carouselItems.length - 1].cloneNode(true);
    lastClone.setAttribute('data-clone', 'first');
    carouselContainer.insertBefore(lastClone, carouselItems[0]);
    
    // Update carouselItems reference
    carouselItems = document.querySelectorAll('.carousel-item');
    
    // Scroll to first real item (index 1) after a brief delay to ensure layout
    setTimeout(() => {
      const itemWidth = carouselItems[1].offsetWidth + 64;
      carouselContainer.scrollLeft = itemWidth;
      currentIndex = 1;
      updateIndicators(); // Update indicators after setting initial position
    }, 100);
  }

  // Get image URL based on screen size
  function getImageUrl(card) {
    const isMobile = window.innerWidth < 768;
    return isMobile ? card.dataset.mobileImg : card.dataset.desktopImg;
  }

  // Update carousel position
  function updateCarousel(direction) {
    if (isScrolling) return;
    isScrolling = true;
    
    // Calculate item width including gap and padding
    const item = carouselItems[0];
    const itemWidth = item.offsetWidth + 64; // width + gap (2rem = 32px) + padding
    
    if (direction === 'next') {
      // If we're at the last real item, jump to cloned first item first (without animation)
      if (currentIndex >= totalItems) {
        carouselContainer.style.scrollBehavior = 'auto'; // Disable smooth scroll for jump
        carouselContainer.scrollLeft = 0; // Jump to cloned first item (instant)
        carouselContainer.style.scrollBehavior = 'smooth'; // Re-enable smooth scroll
        // Small delay to ensure jump completes before smooth scroll
        setTimeout(() => {
          currentIndex = 1; // Set directly to 1 (first real item)
          carouselContainer.scrollBy({
            left: itemWidth,
            behavior: 'smooth'
          });
          updateIndicators(); // Update indicators after currentIndex is set correctly
        }, 10);
      } else {
        currentIndex++;
        carouselContainer.scrollBy({
          left: itemWidth,
          behavior: 'smooth'
        });
        updateIndicators();
      }
    } else if (direction === 'prev') {
      // If we're at the first real item, jump to cloned last item first (without animation)
      if (currentIndex <= 1) {
        const lastPosition = (carouselItems.length - 1) * itemWidth;
        carouselContainer.style.scrollBehavior = 'auto'; // Disable smooth scroll for jump
        carouselContainer.scrollLeft = lastPosition; // Jump to cloned last item (instant)
        carouselContainer.style.scrollBehavior = 'smooth'; // Re-enable smooth scroll
        // Small delay to ensure jump completes before smooth scroll
        setTimeout(() => {
          currentIndex = totalItems; // Set directly to totalItems (last real item)
          carouselContainer.scrollBy({
            left: -itemWidth,
            behavior: 'smooth'
          });
          updateIndicators(); // Update indicators after currentIndex is set correctly
        }, 10);
      } else {
        currentIndex--;
        carouselContainer.scrollBy({
          left: -itemWidth,
          behavior: 'smooth'
        });
        updateIndicators();
      }
    } else {
      carouselContainer.scrollTo({
        left: currentIndex * itemWidth,
        behavior: 'smooth'
      });
      updateIndicators();
    }
    
    updateButtons();
    
    // Wait for scroll to complete before allowing next scroll
    setTimeout(() => {
      isScrolling = false;
      handleInfiniteScroll();
    }, 600);
  }

  // Handle infinite scroll jump (only for manual scrolling, not button clicks)
  function handleInfiniteScroll() {
    const item = carouselItems[0];
    const itemWidth = item.offsetWidth + 64; // width + gap + padding
    const scrollLeft = carouselContainer.scrollLeft;
    const threshold = 50; // pixels threshold for detecting scroll position
    
    // If scrolled to the cloned last item, jump to real first item
    if (scrollLeft >= (carouselItems.length - 1) * itemWidth - threshold) {
      carouselContainer.style.scrollBehavior = 'auto';
      carouselContainer.scrollLeft = itemWidth;
      carouselContainer.style.scrollBehavior = 'smooth';
      currentIndex = 1;
      updateIndicators();
    }
    // If scrolled to the cloned first item, jump to real last item
    else if (scrollLeft <= threshold && currentIndex === 0) {
      carouselContainer.style.scrollBehavior = 'auto';
      carouselContainer.scrollLeft = (carouselItems.length - 2) * itemWidth;
      carouselContainer.style.scrollBehavior = 'smooth';
      currentIndex = totalItems;
      updateIndicators();
    }
  }

  // Update indicators
  function updateIndicators() {
    let displayIndex = currentIndex;
    
    // Map cloned indices to real indices
    if (displayIndex === 0) {
      displayIndex = totalItems; // Cloned last item = real last item
    } else if (displayIndex === carouselItems.length - 1) {
      displayIndex = 1; // Cloned first item = real first item
    }
    
    // Convert to 0-based index for indicators
    // Real items are at indices 1, 2, 3... (totalItems)
    // Indicators are at indices 0, 1, 2... (totalItems - 1)
    let indicatorIndex;
    if (displayIndex >= 1 && displayIndex <= totalItems) {
      indicatorIndex = displayIndex - 1; // Map 1->0, 2->1, 3->2, etc.
    } else {
      // Fallback for edge cases
      indicatorIndex = (displayIndex - 1 + totalItems) % totalItems;
    }
    
    // Ensure indicatorIndex is within valid range
    indicatorIndex = Math.max(0, Math.min(indicatorIndex, totalItems - 1));
    
    indicators.forEach((indicator, index) => {
      if (index === indicatorIndex) {
        indicator.classList.add('active');
      } else {
        indicator.classList.remove('active');
      }
    });
  }

  // Update navigation buttons (always enabled for infinite scroll)
  function updateButtons() {
    prevBtn.disabled = false;
    nextBtn.disabled = false;
  }

  // Open modal with image
  function openModal(index) {
    currentModalIndex = index;
    // Get the real item (index + 1 because first item is clone)
    const realItemIndex = index + 1;
    const card = carouselItems[realItemIndex]?.querySelector('.screenshot-card');
    if (!card) return;
    const imageUrl = getImageUrl(card);
    
    if (!imageUrl || imageUrl.includes('None')) {
      console.warn('No image URL found for this item');
      return;
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Show loading
    modalImage.classList.remove('loaded');
    modalImage.style.display = 'none';
    
    // Load image
    const img = new Image();
    img.onload = function() {
      modalImage.src = imageUrl;
      modalImage.classList.add('loaded');
      modalImage.style.display = 'block';
    };
    img.onerror = function() {
      console.error('Failed to load image:', imageUrl);
      modalImage.alt = 'Image not found';
    };
    img.src = imageUrl;
    
    updateModalButtons();
  }

  // Close modal
  function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
    modalImage.classList.remove('loaded');
  }

  // Update modal navigation buttons
  function updateModalButtons() {
    modalPrev.style.display = currentModalIndex === 0 ? 'none' : 'flex';
    modalNext.style.display = currentModalIndex === totalItems - 1 ? 'none' : 'flex';
  }

  // Navigate modal
  function navigateModal(direction) {
    if (direction === 'prev' && currentModalIndex > 0) {
      currentModalIndex--;
    } else if (direction === 'next' && currentModalIndex < totalItems - 1) {
      currentModalIndex++;
    }
    openModal(currentModalIndex);
  }

  // Event listeners
  prevBtn.addEventListener('click', () => {
    updateCarousel('prev');
  });

  nextBtn.addEventListener('click', () => {
    updateCarousel('next');
  });

  // Indicator clicks
  indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
      const targetIndex = index + 1; // +1 because we start at index 1
      const itemWidth = carouselItems[0].offsetWidth + 64;
      currentIndex = targetIndex;
      isScrolling = true;
      carouselContainer.scrollTo({
        left: targetIndex * itemWidth,
        behavior: 'smooth'
      });
      updateIndicators();
      setTimeout(() => {
        isScrolling = false;
      }, 600);
    });
  });

  // Screenshot card clicks - attach to all items including clones
  function attachCardClicks() {
    document.querySelectorAll('.screenshot-card').forEach((card) => {
      // Get the real index (skip cloned items)
      const item = card.closest('.carousel-item');
      const itemIndex = Array.from(item.parentNode.children).indexOf(item);
      let realIndex;
      
      if (itemIndex === 0) {
        realIndex = totalItems - 1; // First clone = last real item
      } else if (itemIndex === carouselItems.length - 1) {
        realIndex = 0; // Last clone = first real item
      } else {
        realIndex = itemIndex - 1; // Real items offset by 1
      }
      
      card.addEventListener('click', () => {
        openModal(realIndex);
      });
    });
  }

  // Modal controls
  modalClose.addEventListener('click', closeModal);
  modalPrev.addEventListener('click', () => navigateModal('prev'));
  modalNext.addEventListener('click', () => navigateModal('next'));

  // Close modal on overlay click
  document.querySelector('.modal-overlay').addEventListener('click', closeModal);

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!modal.classList.contains('active')) return;
    
    if (e.key === 'Escape') {
      closeModal();
    } else if (e.key === 'ArrowLeft') {
      navigateModal('prev');
    } else if (e.key === 'ArrowRight') {
      navigateModal('next');
    }
  });

  // Handle window resize for responsive images
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      if (modal.classList.contains('active')) {
        const card = carouselItems[currentModalIndex].querySelector('.screenshot-card');
        const imageUrl = getImageUrl(card);
        if (imageUrl && !imageUrl.includes('None')) {
          modalImage.src = imageUrl;
        }
      }
    }, 250);
  });

  // Handle scroll events for infinite scroll
  let scrollTimeout;
  carouselContainer.addEventListener('scroll', () => {
    if (!isScrolling) {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        const itemWidth = carouselItems[0].offsetWidth + 64;
        const scrollIndex = Math.round(carouselContainer.scrollLeft / itemWidth);
        
        // Only update if we're not in the middle of a programmatic scroll
        // and the scroll index is different from current index
        if (scrollIndex !== currentIndex && scrollIndex >= 0 && scrollIndex < carouselItems.length) {
          currentIndex = scrollIndex;
          updateIndicators();
        }
        
        // Handle infinite scroll jump (only for manual scrolling)
        handleInfiniteScroll();
      }, 50);
    }
  });

  // Load correct image based on screen size for all carousel items
  function loadCorrectImages() {
    const isMobile = window.innerWidth < 768;
    const allImages = document.querySelectorAll('.screenshot-preview[data-screenshot-img]');
    
    allImages.forEach((img) => {
      const card = img.closest('.screenshot-card');
      if (!card) return;
      
      const imageUrl = getImageUrl(card);
      if (imageUrl && !imageUrl.includes('None')) {
        // Set the image source
        img.src = imageUrl;
      }
    });
  }

  // Load correct images first (before cloning)
  loadCorrectImages();
  
  // Initialize infinite scroll
  setupInfiniteScroll();
  
  // Load images again after cloning (for cloned items)
  setTimeout(() => {
    loadCorrectImages();
  }, 150);
  
  // Attach card click handlers after cloning
  attachCardClicks();
  
  // Update indicators on load
  updateIndicators();
  updateButtons();

  // Reload images on window resize
  let resizeImageTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeImageTimeout);
    resizeImageTimeout = setTimeout(() => {
      loadCorrectImages();
    }, 250);
  });
})();

