//verwijzing naar hammer.js is eruit gehaald,
//maar onderstaande variable is dan wel nodig
var Hammer;

$(document).ready(function() {
  csvDownloadLink();  
  slideBar();
  remember_items();
  regionSecurity(); 
  colorTable(); 
  showDeleteLine();
  checkboxReports();
  groepItems();
  tab_show_all();
  $("#wwvFlowForm").on('submit', function() { showLoading(); });
  apex.message.setThemeHooks({
    beforeShow: function(pMsgType, pElement$){
      //indien er een apex validatie/boodschap komt bij een submit, de loading terug hiden
      hideLoading();
    }
  });

  $('.t-Region, .t-IRR-region').on('apexafterrefresh', function(){
		hRegionId = $(this).attr("id");
		colorTable(hRegionId);
		showDeleteLine(hRegionId); 
		checkboxReports(hRegionId); 
		return false; 
	});
});

function $url(purl){
	//deprecated, nog op te lossen...
	return purl;
}

function App_Id() {
  return $("#pFlowId").val();
}
function page() {
  return $("#pFlowStepId").val();
}
function session() {
  return $("#pInstance").val();
}
var NS4 = false;

function showLoading() {
  $loading = $("<div id='loading'></div>").prependTo("body");
  apex.util.showSpinner($loading);   
}
function hideLoading() {
  $("#loading").remove();
}

function groepItems() { 
  //op eerste item in groep zet je 'Grid / Column CSS classes': groep_master
  //op items die daar moeten bijkomen zet je properties:
  //'Appearance / CSS Classes': groep_detail
  //'Start New Row': No
  //'New Column': No
  $(".groep_master").each(function() {
    hnaar = $(this).find(".t-Form-inputContainer").first();
    //indien element waar we de groep_detail velden naar gaan copieren zelf in een groep_detail zit
    //dan doen we die groep_detail class weg, anders problemen
    hnaar.parent(".groep_detail").removeClass("groep_detail");
    if (hnaar.length == 1) {
      $(this).find(".groep_detail").detach().appendTo(hnaar);
    }
  })  
}

function tab_show_all() {   
  //hieronder voor apex 19.1(CR_SR_TAB_SHOW_ALL en .a-Region-carouselItem) en apex 20.2(SR_TAB_SHOW_ALL en .a-Tabs-panel)
  $(".t-TabsRegion").on('atabsactivate', function(par1, par2) {
    //par1 lijkt event te zijn
    //par2 bevat de huidige tab
    if (par2.active.href == '#CR_SR_TAB_SHOW_ALL' || par2.active.href == '#SR_TAB_SHOW_ALL') {
      $("#TAB_SHOW_ALL").closest(".t-TabsRegion").find(".a-Region-carouselItem,.a-Tabs-panel").show();
    } else {
      $("#TAB_SHOW_ALL").closest(".t-TabsRegion").find(".a-Region-carouselItem,.a-Tabs-panel").hide();  
      $(par2.active.href).show();      
    }  
  });
	
  //hieronder voor apex 5 en vroeger, mag er dan ooit uit
  //de grapjurken van apex doen zelf een opstart van hun tabsysteem met een setTimeout van 50
  //zie apex js-file: theme42.min.js?v=5.0.1.00.06
	if (typeof $().carousel == 'function'){
		setTimeout(function() {
			//$(".t-TabsRegion .t-Tabs-link").on('click', function() {
			//  if ($(this).attr('href') == '#CR_SR_TAB_SHOW_ALL') {
			//    $(this).closest(".t-TabsRegion").find(".a-Region-carouselItem").css('display','block');
			//  } else {
			//    $(this).closest(".t-TabsRegion").find(".a-Region-carouselItem").css('display','');     
			//  } 
			//});

			$(".t-TabsRegion").carousel({
				onRegionChange: function(mode, activeTab) { 
					if ($(activeTab).attr('href') == '#CR_SR_TAB_SHOW_ALL') {
						$("#TAB_SHOW_ALL").closest(".t-TabsRegion").find(".a-Region-carouselItem").css('display','block');
					} else {
						$("#TAB_SHOW_ALL").closest(".t-TabsRegion").find(".a-Region-carouselItem").css('display','');   
					}  
				}
			});
		},400); 
	}
}

function regionSecurity() {
  //pregions is de jquery selector, iets zoals: '#R141256932889070289,#R141259316354070332'
  pregions = $v('P0_REGIONS_READONLY');
  if (pregions) {
    $(pregions).find('*').attr('disabled', 'disabled');
    $(pregions).find(".buttonAction").fadeTo(0,0.5);
    $(pregions).find("button.cancel").removeAttr('disabled');
    //disabled op een link(a) werkt niet
    $(pregions).find("a").each(function() {
      $(this).attr("href_bck", $(this).attr("href"))
             .attr("href", "javascript:void(0)");
    });
  }
  pregions = $v('P0_REGIONS_HIDDEN');
  if (pregions) {
    $(pregions).hide();
  }
}

function inPWA() {
  //geeft true terug indien we in een PWA zitten (progressive web app)
  var hreturn;
  if ( (window.matchMedia('(display-mode: standalone)').matches) || (window.navigator.standalone) ) {
    hreturn = true;
  } else if ( (window.matchMedia('(display-mode: fullscreen)').matches) || (window.navigator.fullscreen) ) {
    hreturn = true;
  } else {
    hreturn = false;
  }
  //  
  return hreturn;
}

function is_touch_device() {
  return !!('ontouchstart' in window);
}

function is_iOS() {
  return navigator.userAgent.match(/iPad|iPhone|iPod/g) ? true : false ;
}

function html5Storage() {
  //http://diveintohtml5.info/storage.html
  //geeft terug of localStorage gesupporteerd wordt of niet in de browser
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}

/* "snelle zoek" */
/* te gebruiken via f_register */
/* standaard wordt er pas gezocht na ingave van 3 karakters, je kan dit aanpassen via(in voorbeeld na "0" karakters): */
/* $( "#PXX_XXXX" ).autocomplete( "option", "minLength", 0 );*/
function get_lov_data(p_TextFieldName, request, response) {
  //De time out is nodig omdat anders de loading nooit wordt getoond
  autocomplete_loading('On');
  setTimeout(function(){ 
    hfield = $( "#"+p_TextFieldName );

    var get = new htmldb_Get( null,html_GetElement('pFlowId').value,'APPLICATION_PROCESS=get_search_lov',page() );

    get.add('P201_CODE', hfield.attr('pvar_lov') );
    get.add('P201_ZOEK', hfield.val() );
    get.add('TEMP_ZOEK', hfield.val() );
    get.add('P201_TAAL', $('#P0_TAAL').val() );
    //max aantal definierbare parameters
    var paramMaxCount = 6;
    //Variabelewaarden doorgeven
    for (var i=1; i <= paramMaxCount; i++){
      get.add('P201_PAR_'+i, $v(hfield.attr('plov_arg'+i)));
    }

    gReturn = get.get('XML');

    if(gReturn){
      if (gReturn.getElementsByTagName("FOUT").length > 0) {
        alert($xml(gReturn, "FOUT"));
      }else{
        //format the xml to json for the jquery autocomplete source
        var hdata = [];
        $(gReturn).find('row').each(function(i) {
          var hrow = {};
          hrow.label = decodeURIComponent($(this).find('col:eq(0)').text());
          hrow.veld1 = decodeURIComponent($(this).find('col:eq(1)').text());
          hrow.value1 = decodeURIComponent($(this).find('col:eq(2)').text());
          hrow.veld2 = decodeURIComponent($(this).find('col:eq(3)').text());
          hrow.value2 = decodeURIComponent($(this).find('col:eq(4)').text());
          hrow.veld3 = decodeURIComponent($(this).find('col:eq(5)').text());
          hrow.value3 = decodeURIComponent($(this).find('col:eq(6)').text());
          hrow.veld4 = decodeURIComponent($(this).find('col:eq(7)').text());
          hrow.value4 = decodeURIComponent($(this).find('col:eq(8)').text());
          hrow.veld5 = decodeURIComponent($(this).find('col:eq(9)').text());
          hrow.value5 = decodeURIComponent($(this).find('col:eq(10)').text());
          hrow.veld6 = decodeURIComponent($(this).find('col:eq(11)').text());
          hrow.value6 = decodeURIComponent($(this).find('col:eq(12)').text());
          hrow.veld7 = decodeURIComponent($(this).find('col:eq(13)').text());
          hrow.value7 = decodeURIComponent($(this).find('col:eq(14)').text());
          hrow.veld8 = decodeURIComponent($(this).find('col:eq(15)').text());
          hrow.value8 = decodeURIComponent($(this).find('col:eq(16)').text());
          hrow.veld9 = decodeURIComponent($(this).find('col:eq(17)').text());
          hrow.value9 = decodeURIComponent($(this).find('col:eq(18)').text());
          hrow.veld10 = decodeURIComponent($(this).find('col:eq(19)').text());
          hrow.value10 = decodeURIComponent($(this).find('col:eq(20)').text());
          //
          hdata.push(hrow);
        });  
      }
    }
     
    response(hdata);  
   }, 1);
}
//Bij Display Only items steekt apex het veld in een span
function setItemValue(pveldNaam, pvalue){
	var hveld = $("#"+ pveldNaam);
	if (hveld.is('span'))
		hveld.text(pvalue);
	else
		hveld.val(pvalue);
}
function f_register(pvar_lov, p_TextFieldName, p_matchColor, p_noMatchColor) {
  hfield = $( "#"+p_TextFieldName );
 	if (hfield.length == 0){
 		return;	 
 	}
  //steek de (extra) parameters als attribuut op het item  
  hfield.attr('pvar_lov',pvar_lov);
  for (var i=4; i < arguments.length; i++){
    hfield.attr('plov_arg'+(i-3), arguments[i]);
  }

  hfield.autocomplete({
      minLength: 3,
      source: function ( request, response ) {
        get_lov_data( this.element.attr('id'), request, response );
      },
      focus: function( event, ui ) {
        return false;
      },
      select: function( event, ui ) {
        $(this).val( ui.item.label );
        setItemValue(ui.item.veld1, ui.item.value1);
        setItemValue(ui.item.veld2, ui.item.value2);
        setItemValue(ui.item.veld3, ui.item.value3);
        setItemValue(ui.item.veld4, ui.item.value4);
        setItemValue(ui.item.veld5, ui.item.value5);
        setItemValue(ui.item.veld6, ui.item.value6);
        setItemValue(ui.item.veld7, ui.item.value7);
        setItemValue(ui.item.veld8, ui.item.value8);
        setItemValue(ui.item.veld9, ui.item.value9);
        setItemValue(ui.item.veld10, ui.item.value10);
        if (typeof f_after_passBack=="function"){
          f_after_passBack( $("#"+$(this).attr("id")).attr("pvar_lov") );
        }
        //steek de returnvelden ook als attribuut
        //dit om bij leegmaken van snelle zoek de return velden te kunen clearen
        $(this).attr("plov_veld1", ui.item.veld1);
        $(this).attr("plov_veld2", ui.item.veld2);
        $(this).attr("plov_veld3", ui.item.veld3);
        $(this).attr("plov_veld4", ui.item.veld4);
        $(this).attr("plov_veld5", ui.item.veld5);
        $(this).attr("plov_veld6", ui.item.veld6);
        $(this).attr("plov_veld7", ui.item.veld7);
        $(this).attr("plov_veld8", ui.item.veld8);
        $(this).attr("plov_veld9", ui.item.veld9);
        $(this).attr("plov_veld10", ui.item.veld10);
        //
        return false;
      },
      response: function( event, ui ) {
        autocomplete_loading('Off');
        if (!ui.content || ui.content.length === 0) {
          $(this).addClass('lov-no-results');
		  
        if (typeof f_autocomplete_notfound=="function")
					f_autocomplete_notfound($(this));
        }
		else {
          $(this).removeClass('lov-no-results');
        }
      },
      change: function ( event, ui) {
        if ($(this).val().length == 0) {
          //indien snelle zoek wordt leeg gemaakt, clearen van de return velden
          setItemValue($(this).attr("plov_veld1"), "");
          setItemValue($(this).attr("plov_veld2"), "");
          setItemValue($(this).attr("plov_veld3"), "");
          setItemValue($(this).attr("plov_veld4"), "");
          setItemValue($(this).attr("plov_veld5"), "");
          setItemValue($(this).attr("plov_veld6"), "");
          setItemValue($(this).attr("plov_veld7"), "");
          setItemValue($(this).attr("plov_veld8"), "");
          setItemValue($(this).attr("plov_veld9"), "");
          setItemValue($(this).attr("plov_veld10"), "");
        }
      }      
  });   
}

function get_omschr_lov(var_sql_code, pzoek, par1,par2,par3,par4,par5,par6,par7) { 
	pstatus = 0;
// Lege zoek wordt opgevangen in de databasefunctie isb.ae_get_omschr. De returnvelden worden namelijk leeggemaakt.
  var getList = new htmldb_Get(null,html_GetElement('pFlowId').value,'APPLICATION_PROCESS=get_omschr_lov',page(),session());

  getList.add('P201_ZOEK', '');
  getList.add('P201_CODE', var_sql_code);
  getList.add('TEMP_ZOEK', $v(pzoek));
  getList.add('P201_PAR_1', $v(par1));
  getList.add('P201_PAR_2', $v(par2));
  getList.add('P201_PAR_3', $v(par3));
  getList.add('P201_PAR_4', $v(par4));
  getList.add('P201_PAR_5', $v(par5));
  getList.add('P201_PAR_6', $v(par6));
  if (par7 != undefined){
  	getList.add('P201_PAR_7', $v(par7));
 	}
  getList.add('P201_TAAL',$v('P0_TAAL'));
  getResult = getList.get();

  if(getResult) {
  	getResult = decodeXML(getResult);
    if (getResult.substr(0,4) == 'Fout') {
    	pstatus = -1;
			get_omschr_lov_error(pzoek, getResult);
    }
		else {
      var empArray = getResult.split("~itemsep~");
      if (empArray[0]) {
      	$x(empArray[0]).value = empArray[1]; 
      	if($x(empArray[0]).tagName == 'SPAN'){
      		$x(empArray[0]).innerText = empArray[1];
      	}
      }
      if (empArray[2]) {
      	$x(empArray[2]).value = empArray[3]; 
      	if($x(empArray[2]).tagName == 'SPAN'){
      		$x(empArray[2]).innerText = empArray[3];
      	}
      }
      if (empArray[4]) {
      	$x(empArray[4]).value = empArray[5]; 
      	if($x(empArray[4]).tagName == 'SPAN'){
      		$x(empArray[4]).innerText = empArray[5];
      	}
      }
      if (empArray[6]) {
      	$x(empArray[6]).value = empArray[7]; 
      	if($x(empArray[6]).tagName == 'SPAN'){
      		$x(empArray[6]).innerText = empArray[7];
      	}
      }
      if (empArray[8]) {
      	$x(empArray[8]).value = empArray[9]; 
      	if($x(empArray[8]).tagName == 'SPAN'){
      		$x(empArray[8]).innerText = empArray[9];
      	}
      }
      if (empArray[10]) {
      	$x(empArray[10]).value = empArray[11]; 
      	if($x(empArray[10]).tagName == 'SPAN'){
      		$x(empArray[10]).innerText = empArray[11];
      	}
      }
      if (empArray[12]) {
      	$x(empArray[12]).value = empArray[13]; 
      	if($x(empArray[12]).tagName == 'SPAN'){
      		$x(empArray[12]).innerText = empArray[13];
      	}
      }
      if (empArray[14]) {
      	$x(empArray[14]).value = empArray[15]; 
      	if($x(empArray[14]).tagName == 'SPAN'){
      		$x(empArray[14]).innerText = empArray[15];
      	}
      }
      if (empArray[16]) {
      	$x(empArray[16]).value = empArray[17]; 
      	if($x(empArray[16]).tagName == 'SPAN'){
      		$x(empArray[16]).innerText = empArray[17];
      	}
      } 
      if (empArray[18]) {
      	$x(empArray[18]).value = empArray[19]; 
      	if($x(empArray[18]).tagName == 'SPAN'){
      		$x(empArray[18]).innerText = empArray[19];
      	}
      }                                               
   }
  } 
  
  if (typeof f_after_passBack=="function"){
  	f_after_passBack(var_sql_code, pstatus);
 	} 
}

function get_omschr_lov_error(pelement, ptekst){
	$("<div id='dialogDiv'></div>")
		.html(ptekst)
		.dialog({
		    title: $('#'+pelement+'_LABEL').text() + ' Foutieve ingave!',
		    modal: true,
			autoOpen: false,
		    dialogClass: 'PortalDialog error no-close',
		    buttons: [{
		      text: 'OK',
		      click : function() {  
		        $(this).dialog("destroy");
		
				if ($('#'+pelement).prop('nodeName') == 'INPUT'){
					setTimeout("$('#"+pelement+"').focus().select()", 10);
				}else{
					setTimeout("$('#"+pelement+"').focus()", 10); 
				}
		      }
			}, {
		      text: 'Ingave wissen',
		      click: function() {
		        $(this).dialog("destroy");
		        $('#'+pelement).val('');
				if($('#'+pelement).prop('nodeName') == 'INPUT'){
					setTimeout("$('#"+pelement+"').focus().select()", 10);
				}else{
					setTimeout("$('#"+pelement+"').focus()", 10); 
				}
		      }
		    }]
	 	});

	$('#dialogDiv').dialog('open');	
}

function autocomplete_loading(pOnOff) {
  //  
  if (pOnOff == 'On') {
    showLoading();    
  } else {
    hideLoading();    
  }
}

function passBackField(pveld_terug, pveld_terug_waarde){
  if (document.getElementById(pveld_terug).value !== '') {
    tmpReturnElement = parent.$x($x(pveld_terug).value);
    if (tmpReturnElement.tagName == 'SPAN') {
      tmpReturnElement.innerHTML = pveld_terug_waarde;
    }
    else if (tmpReturnElement.tagName = 'FIELDSET' && typeof jQuery !== 'undefined' && ($(tmpReturnElement).hasClass('checkbox_group')) || $(tmpReturnElement).hasClass('radio_group')){
      $(tmpReturnElement).find('input').each(function(){
        $(this).prop("checked", (this.value == pveld_terug_waarde));
      });
    }
    else {
      tmpReturnElement.value = pveld_terug_waarde;
    }
  }
}
function passBack(col02,col03,col04,col05,col06,col07,col08,col09,col10,col11){
  //zat vroeger in page 201 zelf.
  var tmpReturnElement;
  //Eventueel paginanummer voorvoegen
  var ptemp = "2345";
  var i=0
  for (i=1;i<=10;i++){
    if ($x("P201_VELD_TERUG_"+i).value != ''){
      if ($x("P201_VELD_TERUG_"+i).value.substr(0,1) != 'P' || ptemp.indexOf($x("P201_VELD_TERUG_"+i).value.indexOf('_')) == -1){
        $x("P201_VELD_TERUG_"+i).value = 'P'+ window.parent.page() +'_'+ $x("P201_VELD_TERUG_"+i).value ;
      }
    }
  }
  //Velden op oorspronkelijk scherm opvullen
  passBackField('P201_VELD_TERUG_1', col02);
  passBackField('P201_VELD_TERUG_2', col03);
  passBackField('P201_VELD_TERUG_3', col04);
  passBackField('P201_VELD_TERUG_4', col05);
  passBackField('P201_VELD_TERUG_5', col06);
  passBackField('P201_VELD_TERUG_6', col07);
  passBackField('P201_VELD_TERUG_7', col08);
  passBackField('P201_VELD_TERUG_8', col09);
  passBackField('P201_VELD_TERUG_9', col10);
  passBackField('P201_VELD_TERUG_10', col11);
  
  if (window.parent.f_after_passBack){
    window.parent.f_after_passBack($v('P201_CODE'))
  }
  
  window.parent.$(".lovDialog").dialog('destroy').remove(); 
  return false;
}
function lov_allowed(pEl, pAlert){
  if ($x(pEl).disabled == true || $x(pEl).type == 'hidden' || $x(pEl).nodeName == 'SPAN'){
  	if (pAlert){
  		alert('Wijziging niet toegestaan');
  	}
    return false;
  }
  return true;
}
/* einde "snelle zoek" */

function decodeXML(pString){
	uriDecoded = decodeURI(pString);
	
	uriDecoded = uriDecoded.replace( /%23/gi, "#" );
	uriDecoded = uriDecoded.replace( /&quot;/gi, "\"" );
	uriDecoded = uriDecoded.replace( /&amp;/gi, "&" );
	uriDecoded = uriDecoded.replace( /&apos;/gi, "'" );
	uriDecoded = uriDecoded.replace( /&lt;/gi, "<" );
	uriDecoded = uriDecoded.replace( /&gt;/gi, ">" );
	
	return uriDecoded;
}
function encodeXML(pString){
	uriEncoded = encodeURI(pString);
	
	uriEncoded = uriEncoded.replace( /#/gi, "%23" );
	uriEncoded = uriEncoded.replace( /\"/gi, "&quot;" );
	uriEncoded = uriEncoded.replace( /&/gi, "&amp;" );
	uriEncoded = uriEncoded.replace( /\'/gi, "&apos;" );
	uriEncoded = uriEncoded.replace( /</gi, "&lt;" );
	uriEncoded = uriEncoded.replace( />/gi, "&gt;" );
	
	return uriEncoded;
}


/*begin chrome download naar csv bug*/
//
//de download link naar csv ziet er als volgt uit: 
//<div class="t-Report-links"><a href="javascript:window.location.href=apex.server.url({p_request: 'FLOW_EXCEL_OUTPUT_R149046769831850376_nl'},43);">Download</a></div>
//href attribuut springt toch naar het object en toont dan lege pagina met url in
//als je achteraaan void(0) toevoegt, is het opgelost
//
function csvDownloadLink() {
  $(".t-Report-links a").each(function(){
    var pthis = $(this);
    if (pthis.attr('href').indexOf('javascript:window.location.href=apex.server.url') != -1) {
      if (pthis.attr('href').indexOf('void(0);') == -1) {
        pthis.attr('href',pthis.attr('href')+'void(0);');      
      }
    }
  })  
}
$('.t-Region, .t-IRR-region').on('apexafterrefresh', function() {
  csvDownloadLink();
});
/*einde chrome download naar csv bug*/


function colorTable(hRegionId) {
  //This function will change the color of the tablerows
  //Requirements:
  //a div element with the id 'kleur' must be present in the first column
  //formatted like: ''<div id="kleur" style="display:none" class="className"></div>''
  //
  //indien een regio id werd opgegeven, enkel uitvoeren voor die regio
  if (hRegionId) {
    hRegionId = '#'+hRegionId;
  } else {
    hRegionId = '';
  }
  $(hRegionId+" [id=kleur]").each(function(index) {
    hclass = $(this).attr("class");
    $(this).closest('tr').children('td').addClass(hclass);
  }); 
}

function refresh_regio(pRegio) {
	if (arguments.length > 1){
		var getList = new htmldb_Get(null, $v('pFlowId'), 'APPLICATION_PROCESS=dummy_proces', page(),session());
		for (var i=1; i < arguments.length; i+=2){
			getList.add(arguments[i], arguments[i+1]);
		}
		getList.get();
	}

	refresh_regio_paginatie(pRegio);
}
function refresh_regio_paginatie(pstatic_id){
	var hselect = $('#'+pstatic_id).find('select[name=X01]');
	var hmin = '';
	var hattributes;
    
	if (hselect.length > 0){
		var hoptions = $('#'+pstatic_id).find('select[name=X01] option');
		
		/* Huidige startlijn ophalen. */
		var hcurrent = $('#'+pstatic_id).find('select[name=X01] option:selected').text();
		
		for (var i = 0, len = hcurrent.length; i < len; i++) {
			if ($.isNumeric(hcurrent[i])){
				hmin = hmin + hcurrent[i];
			}else{
				if (hmin != ''){
					break;
				}
			}
		}
		
		/* Paginate-functie (specifiek voor deze regio) ophalen. */
		haction = hselect.attr('onchange');
		
		/* Overige paginatie-parameters (max, fetched) afleiden. */
		hoptions.each(function(){
						if ($(this).val() != 'current'){
							hattributes = $(this).val();
							return false;
						}
					});

		var hvan = hattributes.indexOf(":") + 1;
		var htot = hattributes.indexOf(",");
		hattributes = hattributes.substr(0, hvan) + hmin + hattributes.substr(htot);		
		haction = haction.replace('$v(this)', hattributes);
      
		eval(haction);
  }else{
    /*Indien geen paginatielijst. Nog steeds refreshen.*/
    /*event.trigger vervangen door region('').refresh()*/
    //apex.event.trigger( "#"+pstatic_id, "apexrefresh" );
    if (apex.region(pstatic_id)) {
      apex.region(pstatic_id).refresh();
    }
	}
}

/* CSS bij showDeleteLine():
.t-Report--rowHighlight .t-Report-report tr.showDeleteLine:hover .t-Report-cell{
	background-color: rgba(255, 61, 61, 0.5)!important;	/*important staat ook al op de hover-kleur*//*
}
*/
function showDeleteLine(hRegionId){  
  //indien een regio id werd opgegeven, enkel uitvoeren voor die regio
  if (hRegionId) {
    hRegionId = '#'+hRegionId;
  } else {
    hRegionId = '';
  }
	//Te verwijderen lijn van een klasse voorzien. 
  $(hRegionId+' .buttonAction.delete').on("mouseover", function(){$(this).closest('tr').addClass('showDeleteLine')})
                           .on("mouseout", function(){$(this).closest('tr').removeClass('showDeleteLine')});
}

function checkboxReports(hRegionId){
  //Vinkjes in de reportheaders toevoegen.
  var hID;
  var hTableID;

  //indien een regio id werd opgegeven, enkel uitvoeren voor die regio
  if (hRegionId) {
    hRegionId = '#'+hRegionId;
  } else {
    hRegionId = '';
  }

  //headers overlopen 
  //regio's met class="noCheckboxInHeader" krijgen geen extra checkbox.
  //OPGELET: Als het een subregio betreft, klasse ook toekennen aan de hoofdregio!
  $(hRegionId + ".t-Region,"+hRegionId + ".t-DialogRegion").not(".noCheckboxInHeader").find('.t-Report-colHead').each(function(){
    hID = $(this).attr('id');
	
    //als er in het id een ' zit krijgen we een fout: uitstrippen
    if (hID) {
      hID = hID.replace(new RegExp("'", 'g'), "");
    }
    //zit er een checkbox in de bijbehorende kolom
    if ($(this).closest('table').find("tr td[headers='"+hID+"']").has('input[type=checkbox]').length > 0){
      hTableID = $(this).closest('table').uniqueId().attr('id');
      //Checkbox toevoegen in de header
	  $(this).html('<div>'+$(this).html()+'</div>');
      $(this).prepend('<input id="'+hID+'" type="checkbox" onclick="checkall_simulateclick(\''+hTableID+'\',\''+hID+'\',this.checked);" />');
    }
	});
}
function checkall_simulateclick(pTableID, pHeaderID, pindChecked) {
	// vinkjes in de tabel aanvinken wanneer op het vinkje in de header geklikt wordt.
	if (pindChecked) {  
		$('#'+pTableID).find('td[headers="'+pHeaderID+'"] input[type=checkbox]').not(':checked').trigger('click'); 
	} else {
		$('#'+pTableID).find('td[headers="'+pHeaderID+'"] input[type=checkbox]:checked').trigger('click'); 
	}
}
function checkall_simulateclick_SID(hhead, hsid, hhead_el) {
// vinkjes aanvinken wanneer op globaal vinkje geklikt wordt bovenaan in de header.
// Vinkjes toevoegen in de header kan door volgend scriptje in de pagina footer op te nemen

//Enkel voor de regio met SID "regio_sid"
//Meerdere regio's:
  if (hhead_el.checked) {
    $('table[sid="'+hsid+'"] [headers="'+hhead+'"] input[type=checkbox]').not(':checked').trigger('click');    
  } else {
    $('table[sid="'+hsid+'"] [headers="'+hhead+'"] input[type=checkbox]:checked').trigger('click');
  }
}

function confirm_delete_final(pRequest, pString){
  if ($v('P0_TAAL') == 'FR') {
    hmessage = "Vous \352tes s\373re que vous voulez continuer avec la suppression?";
  } else {
    hmessage = "Bent u zeker dat u " + pString + " wil verwijderen?";
  }

  if (confirm(hmessage)) {
     for (var i=2; i < arguments.length; i++){
          $x('P' + page() + '_DELETE' + (i-1)).value = arguments[i];
          $x('P0_DELETE' + (i-1)).value = arguments[i];
     }
     doSubmit(pRequest);
  }
}

var Browser = {
  Version: function() {
    var version = 999; // we assume a sane browser
    if (navigator.appVersion.indexOf("MSIE") != -1)
      // bah, IE again, lets downgrade version number
      version = parseFloat(navigator.appVersion.split("MSIE")[1]);
    return version;
  }
}
function $xml(pXmlObject, pTagname, pcol){
	if (!pcol){
		pcol = 0;
	}
	
	var helement = pXmlObject.getElementsByTagName(pTagname)[pcol];
	if (helement){
		if (Browser.Version() < 10)
			return helement.text;
		else
			return helement.textContent;
	}
	else
		return '';
}

function htmlDecode(input){
  var e = document.createElement('div');
  e.innerHTML = input;
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}

function nvl(pvalue, preturn){
  return pvalue == ''?preturn:(pvalue == null?preturn:pvalue);
}

function IsNumeric(strString){
  //  check for valid numeric strings	
  var strValidChars = "0123456789-";
  var strChar;
  var blnResult = true;

  if (strString.length == 0)
		return false;
  //  test strString consists of valid characters listed above
  for (i = 0; i < strString.length && blnResult == true; i++){
    strChar = strString.charAt(i);
    if (strValidChars.indexOf(strChar) == -1){
      blnResult = false;
    }
  }
  return blnResult;
}


function getElementValue(pelementID){
  if (!pelementID)
		return '';

  var helement = $('#'+pelementID);  
  if (!helement)
		return '';

  if (helement.is('input') && helement.attr('type') == 'checkbox')
		return helement.prop('checked') ? 1 : 0;

  if (helement.is('select') && helement.val() == '%null%')
		return '';

  return helement.val();
}
function callMyPopup (var_sql_code,par1,par2,par3,par4,par5,par6,par7) {  
  pass1 = getElementValue(par1);
  pass2 = getElementValue(par2);
  pass3 = getElementValue(par3);
  pass4 = getElementValue(par4);
  pass5 = getElementValue(par5);
  pass6 = getElementValue(par6);
  if (par7 != undefined){
  	pass7 = getElementValue(par7);
  	url = 'f?p='+App_Id()+':201:'+session()+'::201:201,RP:TEMP_ZOEK,P201_CODE,P201_PAR_1,P201_PAR_2,P201_PAR_3,P201_PAR_4,P201_PAR_5,P201_PAR_6,P201_PAR_7:,' + var_sql_code +','+pass1+','+pass2+','+pass3+','+pass4+','+pass5+','+pass6+','+pass7;
  }else{
  	url = 'f?p='+App_Id()+':201:'+session()+'::201:201,RP:TEMP_ZOEK,P201_CODE,P201_PAR_1,P201_PAR_2,P201_PAR_3,P201_PAR_4,P201_PAR_5,P201_PAR_6:,' + var_sql_code +','+pass1+','+pass2+','+pass3+','+pass4+','+pass5+','+pass6;
  }

  //onderstaande roept ook een dialog op met een iframe erin
  //maar iframe is opgeroepen vanuit topframe, dus niet de huidige pagina
  //en dan werkt de passBack niet...
  var $dialog = $('<div class="lovDialog"></div>')
                 .html('<iframe src="' + url + '" width="100%" height="100%" style="min-width: 95%; height:100%;" scrolling="auto"></iframe>')
                 .dialog({
                     autoOpen: false,
                     dialogClass: "ui-dialog--apex",
                     modal: true,
                     closeOnEscape: true,   
                     position: ['center', 'center'],     
                     height: 600,
                     width: 500,
                     hide: true,
                     close: function(event, ui) { $(this).dialog('destroy').remove(); },
                     title: "List of values"
                 });
  $dialog.dialog('open');
}

function escapeCalendar(){
	//deprecated
}


function alert_isb(pcontent, ptitle, pclass){
  $("<div></div>")
    .html(pcontent) 
    .dialog({
      //title: nvl(ptitle, 'Error'), //wegens niet vertaald
      title: ptitle,
      modal: true,
      dialogClass: 'PortalDialog '+nvl(pclass, 'error')
  });
}

function success_isb(pcomment, pdont_fadeout){
	apex.message.showPageSuccess(pcomment);
	if (!pdont_fadeout)
		$('#t_Alert_Success').delay(3000).fadeOut();
}

/*begin slidebar*/
function slideBar(){
	hslides = $(".slide");

  //we zetten de breedtes van de regio's in zoals de gebruiker ze de vorige keer had ingesteld
	if (html5Storage()) {
		//we checken eerst of de regio's in de local storage wel bestaan -> zoneen wordt de opgeslagen breedte verwijderd
		//die breedte tellen we achteraf op bij de resterende regio's
		var htotale_breedte = 0;
		$.each(localStorage, function(key, value){
			var name = key;
			var value = value;
			
			if (name.indexOf('ISBSLIDE_'+App_Id()+'_'+page()) != -1){
				var regio = name.substring(('ISBSLIDE_'+App_Id()+'_'+page()).length+1, name.length);
				if ($('#'+regio).length == 0)
					localStorage.removeItem(name);
				else
					htotale_breedte += parseFloat(value);
			}
		});
		
		//indien de totale breedte vd slide regio's niet 100% is, zijn er regio's verborgen, dus tellen we die breedte op bij de andere
		var add_breedtes = 0;
		if (htotale_breedte < 99.9 || htotale_breedte > 100.1){	//afrondingsmiserie
			add_breedtes = (100 - htotale_breedte) / hslides.length;
		}
		
		for (var i = 0; i < localStorage.length; i++){
			var name = localStorage.key(i);
			var value = localStorage.getItem(localStorage.key(i));
			
			if (name.indexOf('ISBSLIDE_'+App_Id()+'_'+page()) != -1){
				var regio = name.substring(('ISBSLIDE_'+App_Id()+'_'+page()).length+1, name.length);
				$('#'+regio).parent().css({ 'width': (parseFloat(value) + add_breedtes) + '%'});
			}
		}
	}
	
	if (hslides.length > 0){
		hslides_resorted = $(".slide");
		htotal_width = 0;
		
		//alle slides een initiele width in percentages geven
		hslides.each(function() {
			hwidth = Math.round( ( $(this).outerWidth() * 100 / $(this).parent().innerWidth() ) *100)/100;
			$(this).css({'width': hwidth+'%' });
		});
		
		beperk_slides();
		
		//alle slides behalve de eerste zijn resizable
		hslides.slice(1).resizable({
			handles: 'w',
			start: function () {
				hprev = $(this).prev();   
				htotal_width = Math.round( ( ($(this).outerWidth() + hprev.outerWidth()) * 100 / $(this).parent().innerWidth() ) *100)/100;
			}, 
			resize: function () {
				//bereken nieuwe breedtes
				var hwidth_new = Math.round( ( $(this).outerWidth() * 100 / $(this).parent().innerWidth() ) *100)/100;
				var hwidth_prev = htotal_width - hwidth_new; 
				$(this).css({ 'width': hwidth_new + '%' , 'left':0 });
				$(this).prev().css({ 'width': hwidth_prev + '%' });
				
				if (html5Storage()){
					localStorage.setItem('ISBSLIDE_'+App_Id()+'_'+page()+'_'+$(this).children('.t-Region').prop('id'), hwidth_new);
					localStorage.setItem('ISBSLIDE_'+App_Id()+'_'+page()+'_'+$(this).prev().children('.t-Region').prop('id'), hwidth_prev);
				}
			},
			stop: function () {
				//zorgen dat totale width niet boven de 100% uitkomt door afrondingen
				beperk_slides();
				
				//zonder de resize_reports, is de slide(tabblad) hoogte=0...
				if (typeof resize_reports == 'function') {
					resize_reports(0);
				}
			} 
		});
	}
}
//zorgen dat totale width niet boven de 100% uitkomt door afrondingen
function beperk_slides() {
	htotal_100 = 0;
	//resort array: kleinste widths eerst
	hslides_resorted.sort(function(a,b) { 
		if( $(a).width() < $(b).width()) {
			return -1;
		} else {
			return 1;
		}
	});
	hslides_resorted.each(function() {
		hwidthpx = $(this).outerWidth();
		hwidth = Math.round( ( hwidthpx * 100 / $(this).parent().innerWidth() ) *100)/100;      
		//niet kleiner maken dan 20px
		if (hwidthpx < 10) {
			hwidth = Math.round( ( 10 * 100 / $(this).parent().innerWidth() ) *100)/100;      
			//eveneens element aanpassen
			$(this).css({'width': hwidth+'%' })
		}
		htotal_100 = htotal_100 + hwidth;
	});
	if (htotal_100 > 100) {
		//indien meer dan 100%, de laatste (=breedste) beetje verkleinen
		hwidth = Math.round( ( hslides_resorted.last().outerWidth() * 100 / hslides_resorted.last().parent().innerWidth() ) *100)/100;
		hslides_resorted.last().css({'width': ( hwidth - (htotal_100 - 100) ) + '%' })
	}
}
/*einde slidebar*/

function remember_items(){
  if (html5Storage()) {
		//To remember items
		$('.remember_item').change(function(){
			let id = $(this).attr('id'),
				item = 'ISBITEM_'+App_Id()+'_'+id
				value = $v(id);

			if (value.length > 0)
				localStorage.setItem(item, value);
			else
				localStorage.removeItem(item);
		});

		//Timeout omdat de setValue bij apex_items met multiple values niet direct werkt
		setTimeout(function(){
			//Remembered items
			$.each(localStorage, function(key, value){
				if (key.indexOf('ISBITEM_'+App_Id()+'_P'+page()+'_') != -1){
			var item = key.substring(('ISBITEM_'+App_Id()).length + 1, key.length);
					if ($('#'+item).length == 0)
						localStorage.removeItem(key);
					else
						apex.item(item).setValue(value, null, true);//suppress change event
				}
			});
		}, 10);
  }
}

var hqueue_interval;
var hqueue_seconds_start;
var hqueue_seconds;
function showWaiting(pwaiting) {
  //
  //Indien pwaiting = 0, er is GEEN wachtrij
  //Indien pwaiting != 0, er is WEL een wachtrij en pwaiting bevat aantal seconden dat er moet gewacht worden
  //
  //verwijder de eventuele huidige queue
  $('#isb_queue').remove();
  //check queue
  if (pwaiting != 0) {
    //include css file
    if (!$("link[href='/i/isb/alg/css/isb_queue.css?v=1.02']").length) {
      $('<link href="/i/isb/alg/css/isb_queue.css?v=1.02" rel="stylesheet">').appendTo("head");
    }
    //show queue
    hqueue_seconds_start = pwaiting;
    hqueue_seconds = pwaiting;
    var hqueue = '<div id="isb_queue"><div id="isb_queue_region"><div id="isb_queue_text">';
    var htaal = document.documentElement.lang;
    if (htaal == 'nl') {
      hqueue = hqueue + 'Onze excuses, maar het is heel druk momenteel en er is een wachtrij ingesteld';
    } else if (htaal == 'fr') {
      hqueue = hqueue + 'Nous nous excusons, le site est débordé par une importante demande<br>Une file d\'attente a été établie';
    } else {
      hqueue = hqueue + 'We apologize, but it is very busy right now and a queue has been set up';
    }
    //
    hqueue = hqueue + '</div><div id="isb_queue_loader"><div id="isb_queue_line"></div></div>';
    hqueue = hqueue + '<div id="isb_queue_progress"><div id="isb_queue_progress_part" style="width:100%"></div><div class="isb_queue_seconds">'+pwaiting+'</div></div>';
    //
    var hqueue = hqueue + '<div id="isb_queue_text2">';
    if (htaal == 'nl') {
      hqueue = hqueue + 'Gelieve de pagina niet te herladen<br>(dan komt u achteraan)';
    } else if (htaal == 'fr') {
      hqueue = hqueue + 'Veuillez ne pas renouveler la page afin de ne pas perdre votre position';
    } else {
      hqueue = hqueue + 'Please do not reload the page<br>(you will get to the back)';
    }
    hqueue = hqueue + '</div></div></div>';
    $('body').append(hqueue);
    //refresh the queue
    hqueue_interval = setInterval(refreshWaiting, 1000);
  }
}
function refreshWaiting() {
  hqueue_seconds = hqueue_seconds - 1;
  if (hqueue_seconds > 0) {
    //still waiting, update seconds
    $('.isb_queue_seconds').text(hqueue_seconds);
    //update progress
    $('#isb_queue_progress_part').css('width',(hqueue_seconds*100/hqueue_seconds_start)+'%');
  } else {
    //reload page
    clearInterval(hqueue_interval);
    location.reload();
  }
}
