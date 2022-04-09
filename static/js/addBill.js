//Validates the adding of a bill
function validate() {
   var name = document.getElementById("name").value;
   var descritpion = document.getElementById("description").value;
   var category = $('#category').find(":selected").text();
   var div = document.getElementById('errors-addbill');
   var items = $('.input-total').map((_,el) => el.value).get();
   div.innerHTML=""
   //Validates each of the inputs and displays appropriate error message if one of them is not entered
   if(name=="") {
      div.innerHTML += 'Please enter a bill title';
      return false;
   }
   if (descritpion=="") {
      div.innerHTML += 'Please enter a bill description';
      return false;
   }
   if (category=="Select bill category") {
      div.innerHTML += 'Please select a category';
      return false;
   }

   var valid = true;
   var all_zero = true; //Boolean to store whether all the amount boxes were 0
   //Iterates through each of the household members who have been given a bill to pay
   $.each(items , function(index, val) { 
      var decimalCount = 0;
      //If one user has an amount greater than 0, then all_zero is false
      if (parseFloat(val)!=0){
         all_zero = false;
      }
      //If the input space is blank
      if (val==""){
         div.innerHTML += "Please enter an amount";
         valid = false;
         return false;
      }else{
         //Iterates through the input and ensures that it is a 2 decimal number
         for (var i = 0; i<val.length; i++){
            var currentChar = val.charAt(i);
            if (currentChar=="."){
               if (decimalCount ==0 ){
                  decimalCount +=1;
               }else{
                  div.innerHTML += 'Please enter a valid amount';
                  valid =  false;
                  return false
               }
            //If the input contains any characters
            }else if(!(/^\d+$/.test(currentChar))){
               div.innerHTML += 'Please enter a valid amount';
               valid =  false;
               return false
            }
         }
      }
    });
   //If all the amounts entered were 0, the user is told to enter an amount for a user. 
   if ((all_zero == true)&&(valid==true)){
      div.innerHTML += "Please enter an amount other than 0"
      return false;
   }
   return valid;
}