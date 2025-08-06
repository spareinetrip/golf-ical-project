$(document).ready(function() { 
  //alle modals laten sluiten als je er buiten klikt
  $('body').on('click', '.ui-widget-overlay', function () { 
    $('.ui-dialog-content').dialog('close');
  });
  //page transition
  if (typeof page_transition !== 'undefined') {
    if (page_transition === 'Y') {
      //page is loaded, it is safe to hide loading animation
      //$('body').addClass('loading-done');
      //$('.t-Body-main').fadeIn('fast');
      
      //apex doet ook iets met beforeunload ivm extra warning ivm unsaved changes
      //transitie en warning werken niet samen
      //als je op de pagian blijft na warning, is de transite vertrokken
      //slaag er niet in om te testen op die warning (of op hun event)
      //daarom "voorlopig" die warning altijd uitzetten
      apex.page.cancelWarnOnUnsavedChanges();
      
      $(window).on("beforeunload", function() {
        //user has triggered a navigation, show the loading animation
        handlePageTransition();
      });      
      
      apex.jQuery(apex.gPageContext$).on("apexpagesubmit", function() {
        //page is submitted, show the loading animation
        handlePageTransition();
      });      

      apex.message.setThemeHooks({
        beforeShow: function(pMsgType, pElement$){
          //indien er een apex validatie/boodschap komt bij een submit, de transitie terug hiden
          $('.page-loader').hide();
        }
      });
      
    }
  }
  //get message count
  message_count();
});

function handlePageTransition() {
  //$('body').addClass('loading-busy');
  //$('.t-Body-main').fadeOut('fast');
  $('.page-loader').delay(200).fadeIn();  
}

function message_count() {
  //nieuwe messages (aantal) ophalen
  if (page() != '101') {
    apex.server.process(
      'GET_MESSAGE_COUNT',           
      {},
      {
        success: function (pdata) {            
          if (pdata.mode == -1){
            alert_isb(pdata.comment);
          } else {
            var hmessage = $(".pwa-message");
            var hcount = pdata.aantal;
            
            hmessage.attr('data-count', hcount);
            if (hcount != 0) {
              hmessage.addClass("new-messages");
            } else {
              hmessage.removeClass("new-messages");
            }      
          }
        },
        error: function (pdata){
          alert_isb('Unhandled error: '+JSON.stringify(pdata));
        },
        dataType: "json"
      }
    );   
  }
} 
