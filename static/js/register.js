
//Function which takes the inputs from the form and validates them
//to ensure that the inputs match the validation rules for that 
//particular type of input.  
function validate() {
   //Retrieves the inputs from the input fields in the form
   var email = document.getElementById("email").value;
   var name = document.getElementById("name").value;
   var password = document.getElementById("password").value;
   var repassword = document.getElementById("repassword").value;
   var div = document.getElementById('errors'); //Div for the error messages
   div.innerHTML=""

   // Regex expression test for the email address
   var testEmail = /^[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}$/i;
   //Validates the email
   if (!(testEmail.test(email))){
      div.innerHTML += 'Please enter a valid email';
      return false;
   }
   //Validates the input name
   if (name.length<2) {
      div.innerHTML += 'Please enter your name';
      return false;
   }
   //Validates the password
   if (password<8) {
      div.innerHTML += 'Please enter your password, it must be greater than 7 characters';
      return false;
   }
   //Validates the re-entered password
   if (repassword=="") {
      div.innerHTML += 'Please re-enter your password';
      return false;
   }
   //Ensures both passwords match
   if (repassword!=password) {
      div.innerHTML += 'Please make sure your passwords match';
      return false;
   }
   //Creates an ajax post method to send the details to python script 
   var flag = true;
   $.ajax({
      method: "POST",
      url: "/addUser",
      async: false,
      data: { email: email, name: name, password: password, repassword:repassword },
      success:function (data) {
         //If the registration was not successfull
         if (data.message) {
            div.innerHTML += data.message;
            flag = false;
         }
         //If the registration was successful, redirects the user to the login page
         if (data.redirect) {
            window.location.href = data.redirect;
         }
      }
   });
   //Checks if the user was registered
   if (flag==true){
      alert("You have been registered, please login to continue to your account");
   }
   return false;
}