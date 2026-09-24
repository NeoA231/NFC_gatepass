document.addEventListener("DOMContentLoaded", function () {


setupAdminLogout();
setupStudentFilters();
setupAdminConfirmations();


});

/*

* Admin logout confirmation
  */
  function setupAdminLogout() {

  const logoutForm = document.getElementById("adminLogoutForm");

  if (!logoutForm) {
  return;
  }

  logoutForm.addEventListener("submit", function (event) {

  
   const confirmed = window.confirm(
       "Are you sure you want to log out of the admin portal?"
   );

   if (!confirmed) {
       event.preventDefault();
   }
  

  });

}

/*

* Student registry search and filtering
  */
  function setupStudentFilters() {

  const searchInput = document.getElementById("studentSearch");
  const statusFilter = document.getElementById("gatepassFilter");
  const clearButton = document.getElementById("clearFilters");
  const table = document.getElementById("studentTable");
  const noResults = document.getElementById("noStudentResults");

  if (!searchInput || !statusFilter || !clearButton || !table) {
  return;
  }

  const rows = table.querySelectorAll("tbody tr");

  function filterStudents() {

  
   const searchTerm = searchInput.value
       .trim()
       .toLowerCase();

   const selectedStatus = statusFilter.value;

   let visibleRows = 0;

   rows.forEach(function (row) {

       const studentNumber = row.querySelector(".student-number");
       const studentName = row.querySelector(".student-name");
       const status = row.querySelector(".status-pill");

       const numberText = studentNumber
           ? studentNumber.textContent.trim().toLowerCase()
           : "";

       const nameText = studentName
           ? studentName.textContent.trim().toLowerCase()
           : "";

       const matchesSearch =
           numberText.includes(searchTerm) ||
           nameText.includes(searchTerm);

       let matchesStatus = true;

       if (selectedStatus === "registered") {
           matchesStatus =
               status &&
               status.classList.contains("status-active");
       }

       if (selectedStatus === "unregistered") {
           matchesStatus =
               status &&
               status.classList.contains("status-none");
       }

       const shouldShow =
           matchesSearch && matchesStatus;

       row.style.display = shouldShow ? "" : "none";

       if (shouldShow) {
           visibleRows++;
       }

   });

   if (noResults) {
       noResults.hidden = visibleRows !== 0;
   }
  

  }

  searchInput.addEventListener(
  "input",
  filterStudents
  );

  statusFilter.addEventListener(
  "change",
  filterStudents
  );

  clearButton.addEventListener(
  "click",
  function () {

  
       searchInput.value = "";
       statusFilter.value = "all";

       filterStudents();

   }
  

  );

}

/*

* Confirmation for important admin actions
  */
  function setupAdminConfirmations() {

  const confirmationLinks =
  document.querySelectorAll("[data-confirm]");

  confirmationLinks.forEach(function (element) {

  
   element.addEventListener("click", function (event) {

       const message =
           element.getAttribute("data-confirm");

       if (!message) {
           return;
       }

       const confirmed =
           window.confirm(message);

       if (!confirmed) {
           event.preventDefault();
       }

   });
  

  });

  const confirmationForms =
  document.querySelectorAll("[data-confirm-form]");

  confirmationForms.forEach(function (form) {

  
   form.addEventListener("submit", function (event) {

       const message =
           form.getAttribute("data-confirm-form");

       if (!message) {
           return;
       }

       const confirmed =
           window.confirm(message);

       if (!confirmed) {
           event.preventDefault();
       }

   });
  

  });

}
