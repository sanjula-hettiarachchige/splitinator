
//Validates the login variables and displays error messages
function validate() {
   var email = document.getElementById("email").value;
   var password = document.getElementById("password").value;
   var div = document.getElementById('errors');
   div.innerHTML=""

   //Checks if the username field entered is empty
   if( email=="") {
      div.innerHTML += 'Please enter your email';
      return false;
   }
   //Checks if the user has entered a password or not
   if (password=="") {
      div.innerHTML += 'Please enter your password';
      return false;
   }
   //Stores the result of the ajax post request which will return false if
   //the login failed.
   var result = this;
   $.ajax({
      method: "POST",
      url: "/loginCheck",
      async: false,
      data: { email: email, password: password },
      success: function(str) {
         result = str;
     }
   });

   //If the login failed, then the user is asked to check their details again
   if (result['login']=="fail"){
      div.innerHTML += 'Please check your login details';
      return false;
   }else{
      //If the user has passed the login, then they are given access to the dashboard 
      window.location.href = '/dashboard.html';
   }
   
   return true;
}