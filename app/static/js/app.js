// Filter functionality for listings page
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('search');
  const categorySelect = document.getElementById('category');
  const conditionSelect = document.getElementById('condition');
  const locationInput = document.getElementById('location');
  const listingsContainer = document.getElementById('listings-container');
  const noResults = document.getElementById('no-results');

  if (!listingsContainer) return; // Not on listings page

  const cards = Array.from(listingsContainer.querySelectorAll('.card'));

  function filterListings() {
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedCategory = categorySelect ? categorySelect.value : '';
    const selectedCondition = conditionSelect ? conditionSelect.value : '';
    const locationTerm = locationInput ? locationInput.value.toLowerCase() : '';

    let visibleCount = 0;

    cards.forEach(card => {
      const title = card.dataset.title || '';
      const category = card.dataset.category || '';
      const condition = card.dataset.condition || '';
      const location = card.dataset.location ? card.dataset.location.toLowerCase() : '';

      const matchesSearch = !searchTerm || title.includes(searchTerm);
      const matchesCategory = !selectedCategory || category === selectedCategory;
      const matchesCondition = !selectedCondition || condition === selectedCondition;
      const matchesLocation = !locationTerm || location.includes(locationTerm);

      if (matchesSearch && matchesCategory && matchesCondition && matchesLocation) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    // Show/hide no results message
    if (noResults) {
      if (visibleCount === 0) {
        listingsContainer.style.display = 'none';
        noResults.style.display = 'block';
      } else {
        listingsContainer.style.display = 'grid';
        noResults.style.display = 'none';
      }
    }
  }

  // Attach event listeners
  if (searchInput) searchInput.addEventListener('input', filterListings);
  if (categorySelect) categorySelect.addEventListener('change', filterListings);
  if (conditionSelect) conditionSelect.addEventListener('change', filterListings);
  if (locationInput) locationInput.addEventListener('input', filterListings);
});

// Header CTA button redirect
document.addEventListener('DOMContentLoaded', function() {
  const ctaButton = document.querySelector('.site-header .cta');
  if (ctaButton && ctaButton.tagName === 'BUTTON') {
    ctaButton.addEventListener('click', function() {
      window.location.href = '/deposer';
    });
  }
});
