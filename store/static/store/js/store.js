function openNav() {
    document.getElementById("mySidebar").style.width = "25%";
    document.getElementById("main").style.marginLeft = "25%";
  }
  
  function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
  }


const toggleElem = document.querySelector("#toggle");
const toggleParent = document.querySelector(".wrap__toggle")
toggleElem.addEventListener("change", () =>{

    toggleParent.classList.toggle("active");
});


// JS for 5-star rating field
document.addEventListener("DOMContentLoaded", () => {
  const stars = document.querySelectorAll('#star-rating .star-icon');
  const input = document.getElementById('rating-input');

  function updateStars(val) {
    stars.forEach(s => {
      const starVal = parseInt(s.dataset.value, 10);
      s.classList.toggle('fa-solid', starVal <= val);
      s.classList.toggle('fa-regular', starVal > val);
    });
  }

  stars.forEach(star => {
    star.addEventListener('click', () => {
      const val = parseInt(star.dataset.value, 10);
      input.value = val;
      updateStars(val);
    });

    star.addEventListener('mouseover', () => {
      const val = parseInt(star.dataset.value, 10);
      updateStars(val);
    });

    star.addEventListener('mouseout', () => {
      const currentVal = parseInt(input.value, 10);
      updateStars(currentVal);
    });
  });

  // Initialize on page load
  const initial = parseInt(input.value, 10);
  input.value = initial;
  updateStars(initial);
});
