$(document).ready(function () {

  //$("li").addClass("active")
  $("li").click(function () {
    if (!$(this).hasClass("active")) {
      // var c = "login"
      $("li.active").removeClass("active")
      $(this).addClass("active")
    }
  })
  $('.sidenav').sidenav({
    edge: "right"
  });
  $(".update").hide();
  $("tr td:nth-child(1)").hide()
  $("#jobIdHeader").css("display", "none")
  $(".edit").click(function () {
    $(this).attr("disabled", "disabled")
    $(this).parents("tr").find("td:not(:last-child)").each(function (i) {
      if (i == '1') {
        var idname = 'txtTitle';
      } else if (i == '2') {
        var idname = 'txtDescription';
      } else if (i == '3') {
        var idname = 'txtSkills';
      } else if (i == '4') {
        var idname = 'txtSalary';
      } else if (i == '5') {
        var idname = 'txtLocation';
      }
      $(this).html("<input type='text' name='updaterec' id='" + idname + "' class='input-field' value='" + $(this).text() + "'> ")
    })
    $(this).parents('tr').find('.update').show();
    $(this).hide();
    $(this).parents('tr').find('.delete').removeClass('delete').addClass("update");
  })


  $(".update").click(function () {
    var id = $(this).parents('tr').find('td:nth-child(1)').find('input')[0].defaultValue;
    var txtTitle = $("#txtTitle").val();
    var txtDescription = $("#txtDescription").val();
    var txtSkills = $("#txtSkills").val();
    var txtSalary = $("#txtSalary").val();
    var txtLocation = $("#txtLocation").val();
    $.post("/ajax_update", {
      id: id,
      txtTitle: txtTitle,
      txtDescription: txtDescription,
      txtSkills: txtSkills,
      txtSalary: txtSalary,
      txtLocation: txtLocation
    }, function (data) {
      $("#displayMessage").html(data);
      $("#displayMessage").show();
      setTimeout(function () {
        location.reload();
      }, 1000)

    });
  });


  $(document).on("click", ".delete", function () {
    var id = $(this).parents('tr').find('td:nth-child(1)')[0].innerHTML
    $(this).parents("tr").remove();
    $.post("/ajax_delete", {
      id: id
    }, function (data) {
      $("#displayMessage").html(data);
      $("#displayMessage").show();
    });
  });

  function load_data(query) {
    $.ajax({
      url: "/search/" + query,
      method: "GET",
      success: function (data) {
        $('#result').html(data);
        $("#result").append(data.htmlresponse);
      }
    });
  }
  $('#bthSearch').click(function () {
    var search = $("#search_text").val();
    if (search != '') {
      load_data(search);
    } else {
      load_data('1');
    }
  });
});