

$('#myModal').on('shown.bs.modal', function () {
  $('#myInput').trigger('focus')
})

document.querySelector('.search-input').addEventListener('keyup',async function(event){
  let elem = document.getElementById('search-drop-block')
  let input_value = document.querySelector('.search-input').value

  let response = await fetch('/search/?' + new URLSearchParams({
    data: input_value}))
  let data = await response.json();

  if (!data.result){
    console.log('Error respons data')
  } else {
    elem.innerHTML= data.result
    elem.style.display = "block"
  }

  if (!input_value) {
    console.log(input_value)
    elem.style.display = "none"
  }
event.preventDefault();
});

// implemented on jquery AJAX
// document.querySelector('.search-input').addEventListener('keyup', function(event){
//   $.ajax({
//       url: "/search/",
//       data: {'data': document.querySelector('.search-input').value},
//       success: function(data){
//           if (!data.result){
//               console.log('Error respons data')
//           }else{
//             $("#search-drop-block").css('display', 'block');
//             $("#search-drop-block").html(data.result);
//           }
//           if (!document.querySelector('.search-input').value) {
//             $("#search-drop-block").css('display', 'none');
//           }
//       },
//   });
// event.preventDefault();
// });
