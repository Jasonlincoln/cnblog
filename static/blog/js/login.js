$(function () {
    $('#get_valid_code_img').click(function () {
        $(this)[0].src += '?';
    });
//登录验证
    
    $('#btn_submit').click(function () {

        $.ajax({
            url:"",
            type:"post",
            data:{
                user:$('#user').val(),
                pwd:$('#pwd').val(),
                valid_code:$('#valid_code').val(),
                csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val()

            },
            success:function (data) {

                console.log(data);
                if(data.user){
                    console.log(data.user)
                    location.href = '/index/'

                }else{

                    $('.error').text(data.msg).css({'color': 'red', 'font-size':'16px', 'margin-left':'10px'})
                }
            }
        })

    })



});



