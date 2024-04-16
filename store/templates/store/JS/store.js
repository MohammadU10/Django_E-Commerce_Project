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
