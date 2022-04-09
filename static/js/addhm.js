
//Validates the retrieval of an email address from the form
//Also displays an appropriate message if the field is not filled out properly
function validate() {
   var email = document.getElementById("email").value;
   $('#email').val('');
   var error = document.getElementById('errors-addbill');
   var table = document.getElementById('table-entry');
   error.innerHTML = ""; //Div to hold any error statements
   //If the email address has not been entered
   if( email=="") {
      error.innerHTML += 'Please enter your housemates email';
      return false;
   }
   //Stores the result of checking the status of the user with the entered email address
   var result = this;
   $.ajax({
      method: "POST",
      url: "/addUserHh",
      async: false,
      data: {email: email },
      success: function(str) {
         result = str;
     }
   });

   username = result['Name'];
   if (result['Message'] != "True"){
      //If the user was not able to be added to the household, an appropriate message is displayed
      error.innerHTML += result['Message'];
      return false;
   }else{
      //Inserts the new house hold members row into the table
      $('#table-entry tr:last').after('<tr><td>'+email+'</td><td>'+username+'</td></tr>');
      
   }
   return false;
}