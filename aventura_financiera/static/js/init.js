document.addEventListener("DOMContentLoaded", function() {

function t(e) {
  document.getElementById(e).addEventListener("click", () => {
      const s = document.getElementById("glossary-searchbox");
      s.classList.contains("hidden") ? (s.classList.remove("hidden"), s.classList.add("flex")) : s.classList.add("hidden")
  })
}
t("glossary-openner-button");
t("glossary-closing-button");
window.addEventListener("scroll", function() {
  var e = document.querySelector(".navbar-container"),
      s = "py-4",
      n = "py-1",
      l = window.scrollY;
  l > 50 ? (e.classList.remove(s), e.classList.add(n)) : (e.classList.remove(n), e.classList.add(s))
});

function a(e) {
  document.getElementById(e).addEventListener("click", () => {
      const s = document.getElementById("nav-menu");
      s.classList.contains("translate-x-full") ? (s.classList.remove("translate-x-full"), s.classList.add("translate-x-0")) : s.classList.add("translate-x-full"), console.log("menu:", s)
  })
}
a("hamburger-openner-button");
a("hamburger-closing-button");

window.openModal = function (modalId) {
  document.getElementById(modalId).style.display = "block";
  document.getElementsByTagName("body")[0].classList.add("overflow-y-hidden");
};

window.closeModal = function (modalId) {
  document.getElementById(modalId).style.display = "none";
  document
    .getElementsByTagName("body")[0]
    .classList.remove("overflow-y-hidden");
};

// Close all modals when press ESC
document.onkeydown = function (event) {
  event = event || window.event;
  if (event.keyCode === 27) {
    document
      .getElementsByTagName("body")[0]
      .classList.remove("overflow-y-hidden");
    let modals = document.getElementsByClassName("modal");
    Array.prototype.slice.call(modals).forEach((i) => {
      i.style.display = "none";
    });
  }
};
});
