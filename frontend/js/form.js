document.addEventListener("DOMContentLoaded", function () {


setupRegistrationForm();
setupClaimForm();
setupEditStudentForm();
setupEditGatepassForm();


});

/*

* Student registration
  */
  function setupRegistrationForm() {

  const form = document.getElementById("registerForm");

  if (!form) {
  return;
  }

  form.addEventListener("submit", function (event) {

  
   const studentNumber =
       document.getElementById("student_number");

   const fullName =
       document.getElementById("full_name");

   const phone =
       document.getElementById("phone");

   const residence =
       document.getElementById("residence_address");

   const password =
       document.getElementById("password");


   if (!studentNumber.value.trim()) {
       event.preventDefault();
       alert("Please enter your student number.");
       studentNumber.focus();
       return;
   }


   if (!fullName.value.trim()) {
       event.preventDefault();
       alert("Please enter your full name.");
       fullName.focus();
       return;
   }


   if (!phone.value.trim()) {
       event.preventDefault();
       alert("Please enter your phone number.");
       phone.focus();
       return;
   }


   if (!residence.value.trim()) {
       event.preventDefault();
       alert("Please enter your residence address.");
       residence.focus();
       return;
   }


   if (!password.value.trim()) {
       event.preventDefault();
       alert("Please enter a password.");
       password.focus();
       return;
   }


   if (password.value.length < 6) {
       event.preventDefault();
       alert("Password must contain at least 6 characters.");
       password.focus();
       return;
   }
  

  });

}

/*

* Laptop and NFC tag registration
  */
  function setupClaimForm() {

  const form = document.getElementById("claimForm");

  if (!form) {
  return;
  }

  form.addEventListener("submit", function (event) {

  
   const tagUid =
       document.getElementById("tag_uid");

   const laptopModel =
       document.getElementById("laptop_model");

   const serialNumber =
       document.getElementById("serial_number");


   if (!tagUid.value.trim()) {
       event.preventDefault();
       alert("Please enter the NFC tag UID.");
       tagUid.focus();
       return;
   }


   if (!laptopModel.value.trim()) {
       event.preventDefault();
       alert("Please enter the laptop model.");
       laptopModel.focus();
       return;
   }


   if (!serialNumber.value.trim()) {
       event.preventDefault();
       alert("Please enter the laptop serial number.");
       serialNumber.focus();
       return;
   }


   const confirmed = window.confirm(
       "Are you sure you want to register this laptop and NFC tag?"
   );

   if (!confirmed) {
       event.preventDefault();
   }
  

  });

}

/*

* Edit student information
  */
  function setupEditStudentForm() {

  const form =
  document.getElementById("editStudentForm");

  if (!form) {
  return;
  }

  form.addEventListener("submit", function (event) {

  
   const fullName =
       document.getElementById("full_name");

   const phone =
       document.getElementById("phone");

   const residence =
       document.getElementById("residence_address");


   if (!fullName.value.trim()) {
       event.preventDefault();
       alert("Please enter the student's full name.");
       fullName.focus();
       return;
   }


   if (!phone.value.trim()) {
       event.preventDefault();
       alert("Please enter the student's phone number.");
       phone.focus();
       return;
   }


   if (!residence.value.trim()) {
       event.preventDefault();
       alert("Please enter the student's residence address.");
       residence.focus();
       return;
   }


   const confirmed = window.confirm(
       "Are you sure you want to save these student information changes?"
   );

   if (!confirmed) {
       event.preventDefault();
   }
  

  });

}

/*

* Edit gatepass
  */
  function setupEditGatepassForm() {

  const form =
  document.getElementById("editGatepassForm");

  if (!form) {
  return;
  }

  form.addEventListener("submit", function (event) {

  
   const tagUid =
       document.getElementById("tag_uid");

   const laptopModel =
       document.getElementById("laptop_model");

   const serialNumber =
       document.getElementById("serial_number");

   const status =
       document.getElementById("is_active");


   if (!tagUid.value.trim()) {
       event.preventDefault();
       alert("Please enter the NFC tag UID.");
       tagUid.focus();
       return;
   }


   if (!laptopModel.value.trim()) {
       event.preventDefault();
       alert("Please enter the laptop model.");
       laptopModel.focus();
       return;
   }


   if (!serialNumber.value.trim()) {
       event.preventDefault();
       alert("Please enter the laptop serial number.");
       serialNumber.focus();
       return;
   }


   if (status && status.value === "0") {

       const confirmed = window.confirm(
           "You are about to mark this gatepass as inactive. Continue?"
       );

       if (!confirmed) {
           event.preventDefault();
           return;
       }

   }


   const saveConfirmed = window.confirm(
       "Are you sure you want to save these gatepass changes?"
   );

   if (!saveConfirmed) {
       event.preventDefault();
   }
  

  });

}
