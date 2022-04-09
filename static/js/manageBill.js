
//Method that changes the status of a bill to pending payment. 
//Takes the row number of the bill item being placed into pending payment. 
function payBill(id, rowNo) {
   console.log(rowNo);
   //Sends the id of the bill item that needs the status to be changed to the ipdatePp method
   $.ajax({
      method: "POST",
      url: "/updatePp",
      async: false,
      data: { id: id},
      success: function(str) {
         result = str;
      }
   });
   $("#column-left").load(location.href + " #column-left");
   $("#column-right").load(location.href + " #column-right");

   return true;

}