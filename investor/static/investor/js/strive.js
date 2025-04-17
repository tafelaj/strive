$(document).ready(function () {
    //functions for 1st part of deposit modal
    function makeDeposit(amount, account) {
        $('#modalBody').html('Your Deposit of <strong>ZMW ' + amount +'</strong> was initiated from <strong>('+ account +')</strong>. <br>Please enter you PIN on the popup that will appear on your phone to complete your deposit.');
        $('#depositModel').modal('hide');
        $('#depositInstruction').modal('show');

    }

    //pre-submitting the deposit form
    $('#make_deposit').on('click', function (e) {
        e.preventDefault();
        var depositForm = $('#depositForm');
        //alert(depositForm[0][0].value);
       if(depositForm[0].checkValidity())
           //console.log(depositForm[0][1].valueAsNumber);
           //$('#amount').html();
           makeDeposit(depositForm[0][2].valueAsNumber, depositForm[0][1].value);
       else
           //validate form
        depositForm[0].reportValidity();

    });


    //submitting the deposit form
    $('#confirmDeposit').on('click', function (e) {
        e.preventDefault();
        var depositForm = $('#depositForm');
       if(depositForm[0].checkValidity())
           depositForm.submit();
       else
           //validate form
           console.log('validity error');
         $('#depositInstruction').modal('hide');
         $('#depositModel').modal('show');
        depositForm[0].reportValidity();

    });
 //ajax for posting the form
    function createOrder() {
        //console.log("The function was called"); //sanity check
        $.ajax({
            url: "ajax/submit/", //endpoint

            type: "POST", //http method

            data: {product_id: $('#id_product_id').val(), product_quantity: $('#id_product_quantity').val(),
            sale_id: $('#sale_id').val()}, //data sent with the post request

            success: function (json) {
                if (!json.err){
                    if (!json.quantity_error){

                //console.log(json); //log the returned json to the console

               /* for (var i = 0; i < json.length; i++) {
                 //console.log('Everything seems to have worked'); //sanity check
                    $('#sale_id').val(json[0].sale);

                    var num = i + 1
                    $('#tbody').prepend(
                        "<tr><td>" + num  + "</td> <td><h6>"
                        + json[i].product + " </h6></td> <td class='text-right'> " +
                        "<a href='#' class='btn btn-danger btn-sm'> " +
                        "<i class='nc-icon nc-simple-remove'></i> Remove Item " +
                        "</a> </td> </tr>");
                }*/
               $('#sale_id').val(json.sale);
                    $('#tbody').append(
                        "<tr><td>" + json.product_name  + "</td> <td><h6> K"
                        + json.product_price + " </h6></td> <td class='text-right'> " +
                        "<button class='btn btn-danger btn-sm' value="+json.id+"><i class='nc-icon nc-simple-remove' ></i> Remove Item</button>"+
                        "</td></tr>");

                // calculating the total cost
                var cost = $('#sale_cost');
                var value = parseFloat(json.product_price);
                value = value + parseFloat(cost.val());
                cost.val(value);
                var x = parseFloat(cost.val());

                if (x > 0){
                    $('#displayTotal').html('<hr><h6><strong>TOTAL: K' + value +'</strong></h6><hr>');
                }

                //reset the sale form
                document.getElementById('order_form').reset();

                //set focus to the product id field
                $('#id_product_id').focus();
                    }
                else {
                        alert(json.quantity_error);
                        //set  the product id field
                        //$('#id_product_id').val();

                        //set focus to the product id field
                        $('#id_product_quantity').focus();
                    }

                }
                else {
                    alert(json.err);
                    //set focus to the product id field
                    //reset the sale form
                    document.getElementById('order_form').reset();
                    $('#id_product_id').focus();
                }

            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#error').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
            });

    }

 //submit form on submit
    $('#order_form').on('submit', function (event) {
        event.preventDefault();
        //console.log("Form was submitted"); //sanity check
        createOrder();

        });

  //Clean page when 'Done' button is pressed
  $('#done').on('click', function (event) {
      event.preventDefault();
      $('#tbody').html('');
      $('#sale_id').val('');

      var sale_cost = $('#sale_cost');
      alert('Sale Completed: K'+ sale_cost.val() + ' Sold');
      sale_cost.val(0);
      $('#displayTotal').html('');


  });


     //trying to delete a product from the order second attempt
   $(document).on('click','.btn-danger', function (e) {
       //console.log('its dong something');
       e.preventDefault();
       var productSaleId =  $(this).attr('value');
       //console.log(productSaleId);

       $.ajax({
           url: "ajax/productSale/delete",
           type: "POST",
           data: {
               productSaleId: productSaleId
           },

           success: function (json) {
               var tbody = $('#tbody');
               var cost_object = $('#sale_cost');
               var display_totalObject = $('#displayTotal');

               tbody.html('');
               var sale_id = $('#sale_id');
               if (json.msg) {
                   sale_id.val(''); //set it to none when sale object is deleted, to value of sale otherwise
                   alert(json.msg);
                   display_totalObject.html('');
                   cost_object.val(0);
               }

               //trying to handle changing total cost as products are deleted
               var total = 0;

               for (var i = 0; i < json.length; i++) {
                   console.log('Everything seems to have started to be worked'); //sanity check
                   tbody.append(
                       "<tr><td>" + json[i].product_name + "</td> <td><h6> K"
                       + json[i].product_price + " </h6></td> <td class='text-right'> " +
                       "<button class='btn btn-danger btn-sm' value=" + json[i].id + "><i class='nc-icon nc-simple-remove' ></i> Remove Item</button>" +
                       "</td></tr>");
                   total += parseFloat(json[i].product_price);
               }

               //trying to handle changing total cost as products are deleted
               cost_object.val(total);
               if (cost_object.val() > 0) {

               display_totalObject.html('<hr><h6><strong>TOTAL: K' + cost_object.val() + '</strong></h6><hr>');
               console.log(total)
               }

           },

           error : function(xhr,errmsg,err) {
                $('#error').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error " +
                    "Deleting The Item Form The Order: "+errmsg+
                " <a href='' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }


   })

 });



   //Playing around with spinners

    //when Loading the Update All Form
    $('#update_all_anchor').on('click', function (e) {
        $('#update_all_anchor').append('<div class="spinner-grow text-primary" role="status">\n' +
            '<span class="sr-only">Loading...</span>\n' +
            '</div>');
    });


    $(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

});