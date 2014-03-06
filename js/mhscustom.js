$(document).ready(function(){  

$('#navigator').click(function(){
  $('.sidenav').toggleClass('on');
  var doc_width=$(document ).width();
  // $(".sidenav").css({left:260});
  if($(this).text()=="Hide Form")
  {
    $(this).text("Show Form");
  }else{
    $(this).text("Hide Form");
  }
});

var isEdit=false; 

  $( "#search_text" ).animate({
    opacity: 0.1,
    width: "toggle"
    }, 0, function() {
    // Animation complete.
  });


  $("#search_text").keyup(function(event){
      if(event.keyCode == 13){
          $("#search").click();
      }
  });
  
  $('.form-group > input[type="text"]').keyup(function(event){
    //alert("EnetrKey is Pressed");
    if(event.keyCode==13){
       $("#subbut").click();
    }
  });

  $(".alignment .btn").click(function() {
      // whenever a button is clicked, set the hidden helper
      $(".alignment").find("button").removeClass("active");
      $(this).addClass("active"); 
      //alert("1"+$(this).text()+"1");
      if($(this).text().trim()=="Link")
      {
        $("#linkordesc").html("Link:");

      }
      else{
        $("#linkordesc").html("Description:");
      }
      $("#data_type").val($(this).text().trim());
  }); 
      
  $(".a_modal").click(function(){
    $(".modal_title").text($(this).parent().next("td").text());
    $("#modal_desc").text($(this).parent().siblings("td:eq(1)").text());
    $("#modal_type").text($(this).parent().siblings("td:eq(2)").text());
    $("#modal_date").text($(this).parent().siblings("td:eq(3)").text());
    $("#modal_addedon").text($(this).parent().siblings("td:eq(4)").text());
    $("#modal_delete").attr("href","/delete?Key="+$(this).parent().siblings("td:eq(5)").text());
    $("#modal_key").val($(this).parent().siblings("td:eq(5)").text());
    $("#myModal").modal();
  });

  $(".a_modal").css("cursor","pointer");
  $('#data_table tr *:nth-child(6)').css('display','none');

  $('[data-toggle=offcanvas]').click(function() {
    $('.row-offcanvas').toggleClass('active');
  });
  
  $('#subbut').click(function(){
      /*$('#subbut').toggleClass("btn-default btn-primary disabled");*/
      var url="/main";
      if(isEdit==true)
      {
        url="/update";
      }
      if($("#data_title").val()=="")
      {
        alert("Please enter Title");
        return false;
      }
      else if($("#data_description").val()=="")
      {
        alert("Please enter Description.");
        return false;
      }
      else if($("#data_date").val()=="")
      {
        alert("Please enter Date.");
        return false;
      }
      $('#subbut').text("Sending . . .");
      $('#subbut').addClass("transition");
      var data_type=$("#data_type").val();
      var data_title=$("#data_title").val();
      var data_description=$("#data_description").val();
      var data_date=$("#data_date").val();
      var key = $("#modal_key").val();
      $.ajax(url,{
        type: 'POST',
        data: {data_type:data_type,data_title:data_title,data_description:data_description,data_date:data_date,Key:key},
        success: function(data,status){
                 //alert(data.data_type);
                 //alert("status"+status);
                 //alert(data_type);
                 $('#subbut').addClass("btn-success");
                 $('#subbut').text("Saved");
                 $('#subbut').removeClass("btn-primary active disabled btn-success");
                 $('#subbut').text("Submit");
                 $('#subbut').addClass("btn-primary");
                 var eye_view = '<tr><td align="center" width="5px"><span style="cursor: pointer;" class="a_modal"><span class="glyphicon glyphicon-eye-open"></span></span></td><td>';
                 if(data_type.toLowerCase()=="link")
                 {
                   var link = data_description;
                   if((data_description.substring(0,7)=="http://")|(data_description.substring(0,8)=="https://"))
                   {
                     
                   }
                   else
                   {
                     link="http://" + link;
                   }
                  data_title='<a target="_blank" href="'+link+'">'+data_title+'</a>';
                 }
                 var new_row=$("#data_table tbody tr:first").before(eye_view+data_title+"</td><td>"+data_description+"</td><td>"+data_type+"</td><td>"+data_date+"</td></tr>");
                 $("#data_table tbody tr:first").hide();
                 $("#data_table tbody tr:first").fadeIn("slow");
                 //window.location.reload();
               }
             });
      //$('#subbut').text("Submit");
      //alert("Sorry for the inconvinience the data is failed to send the data to server");
      isEdit=false;
      return false;
  });
var search=false;
  $( "#search" ).hover(function() {
    if(search==false)
    {
      $( "#search_text" ).animate({
        opacity: 1,
        width: "toggle"
      }, "linear", function() {
        // Animation complete.
        $( "#search_text" ).focus();
        search=true;
      });
    }
  });

  $( "#search" ).click(function() {
      var search_text=$( "#search_text" ).val();
      window.open("/search?keyword="+search_text,"_self");
      //alert(search_text);
      search=false;
  });

  $( "#search_text" ).blur(function() {   
      $( "#search_text" ).animate({
        opacity: 0.1,
        width: "toggle"
      }, 400,function() {
        // Animation complete.
        search=false;
      
      });
  });
  
  $("#modal_edit").click(function(){
      //alert($("#data_type").val());
      $("#data_title").val($("#modal_title_label").text().trim()) ;
      $("#data_description").val($("#modal_desc").text().trim());
      $("#data_type").val($("#modal_type").text().trim());
      $("#data_date").val($("#modal_date").text().trim());
      // alert($("#modal_desc").text().trim());
      // alert($("#data_type").val());
      $("#data_title").focus();
      isEdit=true;
  });
  
  $("#modal_edit").css("cursor","pointer");

}); //End of Document Load Jquery 