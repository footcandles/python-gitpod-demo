$(document).ready(function(){
    $('.sidenav').sidenav({edge:"right"});
    $(".edit").click(function(){
      $(this).attr("disabled","disabled")
      $(this).parents("tr").find("td:not(:last-child)").each(function(i){
        if(i=='0'){
          var idname = 'txtTitle';
        }
        else if(i=='1'){
          var idname = 'txtDescription';
        }
        else if(i=='2'){
          var idname = 'txtSkills';
        }
        else if(i=='3'){
          var idname = 'txtSalary';
        }
        else if(i=='4'){
          var idname = 'txtLocation';
        }
        $(this).html("<input type='text' name='updaterec' id='"+idname+"' class='input-field' value='"+$(this).text()+"'> ")
      })
      $(this).parents('tr').find('.edit').toggle();
    })
  });
      