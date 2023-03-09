$(function() {
    $('#registerform').submit(function(event) {

      // Prevent the form from submitting via the browser's default behavior
      event.preventDefault();

        
      // Get the form data

      var formData = new FormData($(this)[0]);
        
      // Send the data via AJAX
      $.ajax({
        url: '/register',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          // Handle the response from the server
          if (response.status_cd==2){
            alert("Email already registered")
          }
          else {
            var newRow = '<tr><td>' + response.fullname + '</td><td>' + response.email + '</td><td>' + response.phone + '</td><td><a href="/users/'+ response.user_id +'">view</a></td></tr>';
            $('#detailstb tbody').append(newRow);
          }
        },
        error: function(jqXHR, textStatus, errorThrown) {
          // Handle any errors that occurred during the request
        }
      });
    });
  });
  




// var complete = function(source) {

//     $.ajax({
//       type: "POST",
//       contentType: "application/json; charset=utf-8",
//       url: "http://127.0.0.1:8000/register",
//       data: JSON.stringify({ sentence: source}),
//       success: function (data) {
  
//         // empty old translations, if any
//         $("#suggested").empty();
  
//         // Show translations on the suggestions list
//         $.each(data.suggestions, function(i) {
//           $("<a>", {
//               id: "alternative",
//               class: "dropdown-item",
//               onclick: "$('#source').val($(this).val().trim()+' ').focus(); $('#suggested').hide();",
//               text: data.suggestions[i],
//               val: data.prefix + " " + data.suggestions[i]
//           }).appendTo("#suggested");
//         });
  
//       },
//       dataType: "json",
//     });
//   }