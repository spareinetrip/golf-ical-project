var message_count_interval;
$(document).ready(function() { 
  //acties uit te voeren na laden van de pagina
  alertMessage();
  pageTitle(); 
  extraFuncs();
  serviceWorker();
  //alleen uit te voeren indien in portal-app
  if ($("#portal_body").length == 1) {
    activatePortalMenu();
    activatePortalFavoriteMenu();
    checkWindowWidth();
    floatWindows();
    portalDashboard();
    pushBericht();
    iOS();
    portal_message_count();
    message_count_interval = setInterval(function(){ portal_message_count('blink') }, 1*60*1000); //iedere minuut checken
  }
});
 
function rel_to_abs(url){
  //Only accept commonly trusted protocols:
  //Only data-image URLs are accepted, Exotic flavours (escaped slash,
  //html-entitied characters) are not supported to keep the function fast 
  if(/^(https?|file|ftps?|mailto|javascript|data:image\/[^;]{2,9};):/i.test(url))
    return url; //Url is already absolute

  var base_url = location.href.match(/^(.+)\/?(?:#.+)?$/)[0]+"/";
  if(url.substring(0,2) == "//")
    return location.protocol + url;
  else if(url.charAt(0) == "/")
    return location.protocol + "//" + location.host + url;
  else if(url.substring(0,2) == "./")
    url = "." + url;
  else if(/^\s*$/.test(url))
    return ""; //Empty = Return nothing
  else url = "../" + url;

  url = base_url + url;
  var i=0
  while(/\/\.\.\//.test(url = url.replace(/[^\/]+\/+\.\.\//g,"")));

  /* Escape certain characters to prevent XSS */
  url = url.replace(/\.$/,"").replace(/\/\./g,"").replace(/"/g,"%22")
          .replace(/'/g,"%27").replace(/</g,"%3C").replace(/>/g,"%3E");
  return url;
}

function activatePortalMenu() {
  //portal accordian menu activeren
  $("#accordian a").click(function(){
    var link = $(this);
    var closest_ul = link.closest("ul");
    var parallel_active_links = closest_ul.find(".active");
    var closest_li = link.closest("li");
    var link_status = closest_li.hasClass("active");
    var count = 0;

    closest_ul.find("ul").slideUp(function(){
      if(++count == closest_ul.find("ul").length)
        parallel_active_links.removeClass("active");
    });

    if(!link_status) {
      closest_li.children("ul").slideDown(function() {
        closest_li.addClass("active");
      });
    }

    //close other accordian
    if (link.parents('#accordianFavorite').length) {
      $("#accordian .active").removeClass("active")
      $("#accordian ul ul").slideUp();
    } else {
      $("#accordianFavorite .active").removeClass("active")
      $("#accordianFavorite ul ul").slideUp();
    }    
  })
}

function activatePortalFavoriteMenu() {
  //portal favorite activeren
  $("#accordianFavorite a").click(function(){
    var link = $(this);
    var closest_ul = link.closest("ul");
    var parallel_active_links = closest_ul.find(".active");
    var closest_li = link.closest("li");
    var link_status = closest_li.hasClass("active");
    var count = 0;

    closest_ul.find("ul").slideUp(function(){
      if(++count == closest_ul.find("ul").length)
        parallel_active_links.removeClass("active");
    });

    if(!link_status) {
      closest_li.children("ul").slideDown(function() {
        closest_li.addClass("active");
      });
    }

    //close other accordian
    if (link.parents('#accordianFavorite').length) {
      $("#accordian .active").removeClass("active")
      $("#accordian ul ul").slideUp();
    } else {
      $("#accordianFavorite .active").removeClass("active")
      $("#accordianFavorite ul ul").slideUp();
    }    
  })
  //
  //make favorites sortable
  //indien item naar links wordt gesleept = een delete
  var hremoveIntent = false;
  $("#accordianFavorite ul ul").sortable({
    placeholder: "placeholder",
    forcePlaceholderSize: true,
    sort: function (event, ui) {   
      if ( ( (ui.position.left - ui.originalPosition.left) < -80) && (Math.abs(ui.position.top - ui.originalPosition.top) < 10) ) {
        removeIntent = true;
        ui.placeholder.addClass("DelFav");
      } else {
        removeIntent = false;
        ui.placeholder.removeClass("DelFav");
      }      
    },
    beforeStop: function (event, ui) {
      if(removeIntent == true){
        ui.item.remove();   
        DelFavorite(ui.item.attr("data-favid"));
      }
    },
    update: function (event, ui) {
      DropFavorite(ui.item.attr("data-favid"),nvl(ui.item.prev().attr("data-favid"),''));
    }
  });  
}

function AddFavorite(pfavid) {
	$('#P0_APP_PROC').val('ADD_FAVORITE');
	$('#P0_FAVID').val(pfavid);

	apex.server.process(
		'isb_xml',
		{pageItems: '#P0_APP_PROC'
							+',#P0_FAVID'
		},
		{
			success: function (pdata) {
				var herror = $xml(pdata, "FOUT");
				if (herror)
					alert_isb(herror);
			},
			error: function (pdata){
				alert_isb('Unhandled error: '+JSON.stringify(pdata));
			},
			complete: function (pdata){
				RefreshFavorite();
			},
			dataType: "xml"
		}
	);
}

function DropFavorite(pfavid, pfav_drop) {
	$('#P0_APP_PROC').val('DROP_FAVORITE');
	$('#P0_FAVID').val(pfavid);
  $('#P0_FAV_DROP').val(pfav_drop);

	apex.server.process(
		'isb_xml',
		{pageItems: '#P0_APP_PROC'
							+',#P0_FAVID'
							+',#P0_FAV_DROP'
		},
		{
			success: function (pdata) {
				var herror = $xml(pdata, "FOUT");
				if (herror)
					alert_isb(herror);
			},
			error: function (pdata){
				alert_isb('Unhandled error: '+JSON.stringify(pdata));
			},
			dataType: "xml"
		}
	);
}

function DelFavorite(pfavid) {
	$('#P0_APP_PROC').val('DEL_FAVORITE');
	$('#P0_FAVID').val(pfavid);

	apex.server.process(
		'isb_xml',
		{pageItems: '#P0_APP_PROC'
							+',#P0_FAVID'
		},
		{
			success: function (pdata) {
				var herror = $xml(pdata, "FOUT");
				if (herror)
					alert_isb(herror);
			},
			error: function (pdata){
				alert_isb('Unhandled error: '+JSON.stringify(pdata));
			},
			complete: function (pdata){
				//indien er geen favorites meer zijn, dan verwijderen van favorites menu-item
				//lengte testen op 1 ipv 0, want item is blijkbaar nog niet weg
				if ($("#accordianFavorite ul ul li").length <= 1) {
					RefreshFavorite();
				}
			},
			dataType: "xml"
		}
	);
}

function RefreshFavorite() {
	apex.server.process(
		'show_favorites',
		{pageItems: '#P0_TAAL'
		},
		{
			success: function (pdata) {
				$("#accordianFavorite").replaceWith(pdata);
				//door replaceWith zijn de events weg, dus opnieuw uitvoeren
				activatePortalFavoriteMenu();
			},
			error: function (pdata){
				if (pdata)
				  alert_isb('Unhandled error: '+pdata);
			},
			dataType: "text"
		}
	);
}

function activateHelpMenu() {
  //portal help accordian menu activeren
  $("#accordianHelp a").click(function(){
    var link = $(this);
    var closest_ul = link.closest("ul");
    var parallel_active_links = closest_ul.find(".active")
    var closest_li = link.closest("li");
    var link_status = closest_li.hasClass("active");
    var count = 0;

    closest_ul.find("ul").slideUp(function(){
      if(++count == closest_ul.find("ul").length)
        parallel_active_links.removeClass("active");
    });

    if(!link_status) {
      closest_li.children("ul").slideDown(function() {
        closest_li.addClass("active");
      });
    }
  })
}

function getHelpItem(pvolgnr) { 
  $("#HELP_ZOEK").hide();
  //
  $("#HELP_TOPIC").show();
	
	$('#P'+page()+'_HELP_TOPIC').val(pvolgnr);
	
	apex.server.process(
		'refresh_clob',
		{pageItems: '#P'+page()+'_HELP_TOPIC'
		},
		{
			success: function (pdata) {
			},
			error: function (pdata){
				if (pdata)
				  alert_isb('Unhandled error: '+pdata);
			},
			complete: function (pdata){
				$(".help_topic").html(pdata).highlight($v('P'+page()+'_SEARCH'), 'hilite');
				$(window).scrollTop(0);
			},
			dataType: "text"
		}
	);
}
//
//extend jQuery with a higlight
//surrounds the "str" with "className"
//http://beatgates.blogspot.be/2011/07/extend-jqueryhighlight-to-highlight.html
//
jQuery.fn.highlight = function(pattern, className) {
  if (pattern) {
    var regex = typeof(pattern) === "string" ? new RegExp(pattern, "i") : pattern; // assume very LOOSELY pattern is regexp if not string
    function innerHighlight(node, pattern) {
      var skip = 0;
      if (node.nodeType === 3) { // 3 - Text node
        var pos = node.data.search(regex);
        if (pos >= 0 && node.data.length > 0) { // .* matching "" causes infinite loop
          var match = node.data.match(regex); // get the match(es), but we would only handle the 1st one, hence /g is not recommended
          var spanNode = document.createElement('span');
          spanNode.className = className; // set css
          var middleBit = node.splitText(pos); // split to 2 nodes, node contains the pre-pos text, middleBit has the post-pos
          var endBit = middleBit.splitText(match[0].length); // similarly split middleBit to 2 nodes
          var middleClone = middleBit.cloneNode(true);
          spanNode.appendChild(middleClone);
          // parentNode ie. node, now has 3 nodes by 2 splitText()s, replace the middle with the highlighted spanNode:
          middleBit.parentNode.replaceChild(spanNode, middleBit); 
          skip = 1; // skip this middleBit, but still need to check endBit
        }
      } else if (node.nodeType === 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) { // 1 - Element node
        for (var i = 0; i < node.childNodes.length; i++) { // highlight all children
          i += innerHighlight(node.childNodes[i], pattern); // skip highlighted ones
        }
      }
      return skip;
    }
     
    return this.each(function() {
      innerHighlight(this, pattern);
    });
  }
};
// 
jQuery.fn.removeHighlight = function(className) {
  return this.find("span."+className).each(function() {
    this.parentNode.firstChild.nodeName;
    with (this.parentNode) {
      replaceChild(this.firstChild, this);
      normalize();
    }
  }).end();
};

function checkWindowWidth(){
	if ($(window).width() >= 1024){
    //tonen van menu
    $("#portal-container, #portal-menu, #portal-page").addClass("menu-active").removeClass("menu-not-active");
  }	else {
    //hide van menu
    $("#portal-container, #portal-menu, #portal-page").removeClass("menu-active").addClass("menu-not-active");
  }
}
 
function openWindow(purl, ptitel, pheight, pwidth, pleft, ptop, pportal_item) {
  purl = decodeXML($url(purl));
  //
  if ( is_touch_device() && ($(window).width() <= 1024) && (typeof portalAppId !== 'undefined') ) {
    //indien we op een touch device zitten EN een klein scherm EN de global portalAppId bestaat
    //dan draaien we nieuwe schermen niet in een iframe, maar rechtstreeks en dan roepen we de portal menu in een iframe op
    //zie ook pageTitle() 
    if (purl.indexOf('ae_portal.get_portal_url_redirect?')!=-1){
      //als het geen apex url is, dan openen in een nieuw window, want anders menu kwijt
      window.open(purl, '_blank');
    } else {
      top.location.href = purl;
    }
  
  } else if (top.$v('P0_IND_FLOAT') != '1' || is_touch_device()) {
    //vast frame	
    top.$("#portal-page>iframe").attr('src', purl);  
    //favoriet knop toevoegen
    hheader = top.$("#portal-header");
    hheader.find(".favorite").remove();
    if (pportal_item) {
      hheader.append($('<div class="favorite" title="add as favorite"></div>')
                         .on('click.portal', function (event) { 
                            //zetten als favorite 
                            top.AddFavorite(pportal_item);
                         })
                      );    
    }
  } else {
    //aparte frames
    //
    //opzoeken van laatst toegekend taskbarWindowId
    //voor alle windows worden de id's in een array gestoken en hieruit wordt max nr gehaald...en dat + 1
    var ptaskbarWindowId = null;
    top.$('.portal-page-float').each(function() {
      var value = parseFloat($(this).attr('id'));
      ptaskbarWindowId = (value > ptaskbarWindowId) ? value : ptaskbarWindowId;
    });
    ptaskbarWindowId = nvl(ptaskbarWindowId, 0) + 1;
    //
    var hfavorite = '';
    if (pportal_item) {
      hfavorite = '  <div class="favorite" title="add as favorite"></div>';
    }
    ptitel = nvl(ptitel,'');
    //
    hfloat = '<div class="portal-page-float normal" id="'+ptaskbarWindowId+'" portal_item="'+pportal_item+'">'+
             '  <iframe class="iframefloat"></iframe>'+
             hfavorite+
             '  <div class="title">'+ptitel+'</div>'+
             '  <div class="window-toggle"></div>'+
             '  <div class="close"></div>'+
             '  <div class="windowcontent">'+
             '    <iframe class="iframecontent" src="'+purl+'"></iframe>'+
             '  </div>'+
             '</div>';
    var w = top.$(hfloat).appendTo('#portal-page');
    //
    w.css({ height: nvl(pheight, '640px'), 
            width: nvl(pwidth, '800px'),
            left: nvl(pleft, '300px'),             
            top: nvl(ptop, '60px'),             
            zIndex: maxZ(".portal-page-float")
          });
    //events toevoegen
    w.find(".favorite").on('click.portal', function (event) { 
      //zetten als favorite 
      top.AddFavorite(pportal_item);
    });
    w.find(".close").on('click.portal', function (event) { 
      //close 
      top.closeWindow(ptaskbarWindowId);
    });
    w.find(".window-toggle").on('click.portal', function (event) { 
      //toggle de class "max"
      top.$(".taskbarTask[data-line="+ptaskbarWindowId+"] .taskbarTaskWindowToggle").toggleClass("max");
      //toggle class "maximize" en "normal" op scherm
      top.$(".portal-page-float[id="+ptaskbarWindowId+"]").toggleClass("maximize normal");
    });
    //in taskbar steken
    top.addToTaskbar(ptaskbarWindowId, pportal_item, ptitel);
    //hoogte, breedte, left en top mogelijks overschrijven via de opgeslagen window storage
    top.recallWindow(ptaskbarWindowId);
    //ook draggable maken
    w.draggable({ 
        handle: ".title", 
        iframeFix: true, 
        containment: "#portal-page", 
        scroll: false, 
        start: function (event, ui) {
          activateTaskbar(ui.helper.attr("id"));
        },
        stop: function(event,ui){
          top.saveWindow(ui.helper.attr("id"));
        }              
    });
    //bij mousedown scherm naar boven brengen
    w.on('mousedown.portal', function () {
      activateTaskbar($(this).attr("id"));
    })
    //ook resizable maken
    w.resizable({ 
        handles: ('n,e,s,w,ne,nw,se,sw'),
        containment: "#portal-page",
        start:function(event,ui){
          activateTaskbar(ui.helper.attr("id"));
          //indien scherm op maximize staat
          if (ui.helper.hasClass("maximize")) {
            //toggle class "maximize" en "normal" op scherm
            ui.helper.toggleClass("maximize normal");
            //toggle de class "max"
            ui.helper.find(".window-toggle").toggleClass("max");
          }
          //          
          top.$("iframe").each(function() {
            top.$('<div class="ui-resizable-iframeFix" style="background: #fff;"></div>')
            .css({
              width: this.offsetWidth+"px", height: this.offsetHeight+"px",
              position: "absolute", opacity: "0.001", zIndex: 1000
            })
            .css($(this).offset())
            .appendTo("body");
          });
        },
        stop: function(event,ui){
          top.$("div.ui-resizable-iframeFix").each(function() { this.parentNode.removeChild(this); }); //Remove frame helpers
          //
          top.saveWindow(ui.element.attr("id"));
        }      
    }); 
    //indien er al vensters gemaximalizeerd staan, dit venster ook maximalizeren
    //altijd maximalizeren    
    //if ($(".portal-page-float.maximize").length != 0) {
    w.find(".window-toggle").trigger('click.portal');    
    //}        
  }
  //
  top.checkWindowWidth();
}

function openHelpWindow(pHelpTopic, ptitle, pheight, pwidth, pleft, ptop, pportal_item){
  var htitle = ptitle?ptitle:'Help';
  //
  openWindow('f?p='+top.App_Id()+':13:'+session()+':::13,RP:P13_HELP_TOPIC:'+pHelpTopic, htitle, pheight, pwidth, pleft, ptop, pportal_item);
}
  
function closeWindow(hid) {
  //opzoeken van id van window
  if (!hid) {
    top.$("iframe").each(function(iel, el) {
      if(el.contentWindow === window.self) {
        hid = $(this).closest('.window').attr('id');
      }
    });
  }
  //
  if (hid) {
    top.$('.portal-page-float#'+hid).fadeOut('100', function () {$(this).remove()});
    top.deleteFromTaskbar(hid);
  } else {
    window.close();
  }
};

function floatWindows() {
  if ($v('P0_IND_FLOAT') == '1') {
    $(".portal-ind-float").addClass("active");
	$("#portal-container").removeClass("fixed").addClass("not-fixed");
  } else {
	$("#portal-container").addClass("fixed").removeClass("not-fixed");
  }
  //
  //close the setting popup 
  //if the document is clicked somewhere
  $(document).on("mousedown.portal-settings touchstart.portal-settings", function (e) {
    // If the clicked element is not the setting or the setting-button
    if (!$(e.target).closest(".portal-settings").length > 0) {
      if (!$(e.target).closest(".portal-settings-btn").length > 0) {
        // Hide it 
        $(".portal-settings").hide();
      }
    }
  });      
} 
 
function maxZ(pselector){
  //calculate highest z-index
  //and add one
  var hmaxZ = Math.max.apply(null,$.map($(pselector), function(e,n){
    return parseInt($(e).css('z-index'))||1 ;
    }) 
  );
  return hmaxZ+1;
}

function pushBericht() {
  if ($v('P20_PUSH_TEKST') != '') {
    var $dialog = $('<div></div>')
                  .html($v('P20_PUSH_TEKST'))
                  .dialog({
                            autoOpen    : false,
                            title       : $v('P20_PUSH_TITEL'),
                            dialogClass : "PortalDialog info no-close",
                            modal       : true,
                            width       : '600',
                            height      : '300',
                            buttons: [
                                        {
                                          text: "Close message",
                                          click: function() {
                                            //$( this ).dialog( "close" );
                                            //standaard close en close van hierboven zorgt voor js error (door iets van de apex toolbar
                                            //vervangen door onderstaande destroy
                                            $( this ).dialog( "destroy" );
                                          }
                                        }
                                      ]
                          });
    $dialog.dialog('open');   
  }
}  

function portalDashboard() {
  //indien er een url is, dan openenen we deze
  purl = $("#portal_dashboard").attr('hurl');
  if (purl) {
    top.$("#portal-page>iframe").attr('src', purl);  
  }
}
 
function inIframe() {
  try {
    return window.self !== window.top;
  } catch (e) {
    return true;
  }
}

function pageTitle() {	
  //opvullen van de titel, refresh knop en print knop  
  //niet voor page 201 (lov)
  var happend = ''; 
  if (page() != 201) {
    //
    //indien we op een touch device zitten EN een klein scherm EN de global portalAppId bestaat EN we zitten in top frame
    //dan draaien we nieuwe schermen niet in een iframe, maar rechtstreeks en dan roepen we de portal menu in een iframe op
    //dan plaatsen we knop om portal menu te openen 
    //zie ook openWindow() 
    if ( is_touch_device() && ($(window).width() <= 1024) && (typeof portalAppId !== 'undefined') && (!inIframe()) ) {
      happend = '<div class="portal-float-menu-bt" onclick="portal_float_menu()">menu</div>';
    }
    //indien het een portal applicatie betreft, extra titel , refresh en print knop toevoegen
    if (typeof portalAppId !== 'undefined') {
      happend = happend + '<div class="title">'+$("title").html()+'</div>'+
                          '<div class="refresh" onclick="portal_refresh()" title="refresh">refresh</div>'+
                          '<div class="print" onclick="portal_print()" title="print">print</div>';
    }
    //
    var p = $(happend).appendTo('.t-Header-logo');    
  }
}  
 
function extraFuncs() {
  //taskbar sortable maken
  //bug in jQuery: extra div: http://stackoverflow.com/questions/19106717/jquery-sortable-doesnt-work-correctly-with-horizontal-list-if-list-is-empty-bef
  $(".portal-taskbar-inner").append('<div id="bug" class="taskbarTask"></div>');
  $(".portal-taskbar-inner").sortable({
    scroll: true,
    //containment: "parent",
    stop: function (event, ui) {
      helem = $(".portal-taskbar-inner").not($(this)).empty();
      $(this).children().clone(true,true).appendTo(helem);
      ui.item.trigger('click');      
    }
  });  
  $(".portal-taskbar-inner #bug").remove();
}

function iOS() {
  //iOs houdt geen rekening met css ivm hoogte 100%, de hoogte wordt aangepast naar de contents door iOS
  //we doen zelfde via css voor de portal menu
  if (is_iOS()) {
    $("#portal-menu").addClass("iOS_menu");   
  }
}

function checkCookies() {
  ts=new Date().getTime();
  document.cookie='ts='+ts;
  var cookies=document.cookie;
  if(!cookies){ 
    var htitle = 'Cookies';
    var hhtml = 'Your cookies seem to be disabled.'+
                '<br>This site will not work until you enable cookies in your browser.';

    if (inIframe()) {
      hhtml = hhtml + '<br>Please also enable third-party cookies.';
      hhtml = hhtml + '<br><br>You can always try to run this site in a new browser:';
      hhtml = hhtml + '<br><a href="'+window.location+'" target="_blank">'+window.location+'</a>';
    }

    var $dialog = $('<div></div>')
                  .html(hhtml)
                  .dialog({
                            autoOpen    : false,
                            title       : htitle,
                            dialogClass : "PortalDialog error",
                            modal       : true,
                            //width       : '600',
                            //height      : '300'
                          });
    $dialog.dialog('open');   
  };
}

function show_hide_tree(pchild) {
  var therows = $("span[par4='tree']");
  t_child = "_"+pchild+"_";
  therows.each(function(i) {
    if (pchild==this.attributes.par2.value){
      tplus_min = this.attributes.par3.value;
      if (tplus_min == "plus")
        {this.attributes.par3.value = "min";
         document.getElementById(this.attributes.par2.value).src="/i/isb/alg/img/rollup_minus_dgray.gif";
        }
      else
        {this.attributes.par3.value = "plus";
         document.getElementById(this.attributes.par2.value ).src="/i/isb/alg/img/rollup_plus_dgray.gif";
      }
    }
    //als de vader vervat zit in de childs dan veranderen van display
    t_father = "_"+this.attributes.par1.value +"_";
    if (t_child.indexOf(t_father) != -1) {
      if (tplus_min == "plus" ) {
        $(this).parents('tr')[0].style.display = "table-row";
        //this.attributes.par3.value = "min";
        //if (document.getElementById(this.attributes.par2.value )) {
        //  document.getElementById(this.attributes.par2.value).src="/i/isb/alg/img/rollup_minus_dgray.gif";
        //  }              
        }
      else {
        $(this).parents('tr')[0].style.display = "none";
        this.attributes.par3.value = "plus";
        if (document.getElementById(this.attributes.par2.value )) {
          document.getElementById(this.attributes.par2.value ).src="/i/isb/alg/img/rollup_plus_dgray.gif";
        }
        t_child = t_child+this.attributes.par2.value +"_";
      }
    }
  });       
}

function collapse_tree() {
  var therows = $("span[par3='min']").not('.tree_niv_0');
  therows.each(function(i) {
    if (document.getElementById(this.attributes.par2.value )) {
      if (this.attributes.par3.value == 'min' ) {
        show_hide_tree(this.attributes.par2.value);
      }
    }
  });       
}

function alertMessage() {
  if ($('#P'+page()+'_MODE').val() == '-1') {
    $('#t_Alert_Success').addClass('isb_error');
  }
  else if ($('#P'+page()+'_MODE').val() == '1') {
    $('#t_Alert_Success').addClass('isb_warning');
  }
	else {
    setTimeout(function() {
			$('#t_Alert_Success').fadeOut();
		}, 5000);
  }
}

function rememberMe() {
  //remember me functionaliteit op de login pagina
  //if ($v('P101_REMEMBER_ME') == '1') {
  //  alert('Are you sure?');
  //} 
}

function clearRememberMe() {
  //verwijderen van de remember me cookies
  $.cookie('ISB_REMEMBER_USER_'+App_Id(),null)
  $.cookie('ISB_REMEMBER_KEY_'+App_Id(),null)
}

function trustMe() {
  //"trust this device" functionaliteit op de TFA pagina
  //if ($v('P23_REMEMBER_ME') == '1') {
  //  alert('Are you sure?');
  //} 
}

function clearTrustMe() {
  //verwijderen van de remember me cookies
  $.cookie('ISB_TRUST_USER_'+App_Id(),null)
  $.cookie('ISB_TRUST_KEY_'+App_Id(),null)
}

function portal_refresh() {
  $("#loading").show();
  location.reload();
}

function portal_print() {
  print();
}

function portal_logout() {
  //
  clearRememberMe();
  clearTrustMe();
  //
  var hurl;
  if (typeof portalAppId !== 'undefined') {
    hurl = 'f?p='+portalAppId+':101';
  } else {
    hurl = 'f?p='+App_Id()+':101';
  }
  //  
  top.location.href = hurl;
}

function portal_menu() {
  $("#portal-container, #portal-menu, #portal-page").toggleClass("menu-active menu-not-active");
}

function portal_float_menu() {
  //togglen van portal iframe menu
  hmenu = $(".portal-menu-float");
  if (hmenu.length == 0) {
    //indien menu nog niet betaat, aanmaken en openen
    hurl = 'f?p='+portalAppId+':21:'+session();
    hmenu = $('<div class="portal-menu-float">'+
              '  <iframe class="iframecontent" src="'+hurl+'"></iframe>'+
              '</div>');
    hmenu.appendTo('body');
    // If the document is clicked somewhere
    $(document).on("mousedown.portal-menu-float touchstart.portal-menu-float", function (e) {
      // If the clicked element is not the menu or the menu-button
      if (!$(e.target).closest(".portal-menu-float").length > 0) {
        if (!$(e.target).closest(".portal-float-menu-bt").length > 0) {
          // Hide it 
          hmenu.hide();
        }
      }
    });    
  } 
  //togglen
  hmenu.toggle();
  //scroll naar boven
  $('html,body').scrollTop(0);  
}

function portal_zoeken() {
  openWindow($url('f?p='+App_Id()+':10:'+session()+':::10,RP:P10_INITIALIZE,P10_ZOEK:1,'+$v('PORTAL_INPUT_ZOEK')),'Search');
}

function portal_zoeken_entered(event) {
  if(event.keyCode=='13'){
    event.preventDefault();
    portal_zoeken();
  }
}

function portal_ind_float() {
  var pind_float;
  if ($v('P0_IND_FLOAT') == '1') {
    $(".portal-ind-float").removeClass("active");
    pind_float = '0';
    $("#portal-container").addClass("fixed").removeClass("not-fixed");
    //verwijderen van openstaande windows
    $(".portal-page-float").remove();
    $(".taskbarTask").remove();
    taskbarButton();	
  }
	else {
    $(".portal-ind-float").addClass("active");
    pind_float = '1';
    $("#portal-container").removeClass("fixed").addClass("not-fixed");
    //
    $("#portal-header .favorite").hide();
  }
	
	$('#P0_APP_PROC').val('SAVEPORTALFLOAT');
	$('#P0_IND_FLOAT').val(pind_float);

	apex.server.process(
		'isb_xml',
		{pageItems: '#P0_APP_PROC'
							+',#P0_IND_FLOAT'
		},
		{
			success: function (pdata) {
				var herror = $xml(pdata, "FOUT");
				if (herror)
					alert_isb(herror);
			},
			error: function (pdata){
				alert_isb('Unhandled error: '+JSON.stringify(pdata));
			},
			dataType: "xml"
		}
	);
}

function portal_message_count(pblink) {
  hurl = $v('P0_MESSAGE_URL'); 
  if (Boolean(hurl)) {
		$('#P0_APP_PROC').val('GET_MESSAGE_COUNT');

		apex.server.process(
			'isb_xml',
			{pageItems: '#P0_APP_PROC'
			},
			{
				success: function (pdata) {
					var herror = $xml(pdata, "FOUT");
					if (herror){
						alert_isb(herror);
					}
					else{
						var hmessage = $(".portal-messages-btn");
						var hcount_prev = hmessage.attr('data-count');
						var hcount = $xml(pdata, "AANTAL");
						
						hmessage.attr('data-count', hcount).removeClass("blink");;
						if (hcount != 0) {
							hmessage.addClass("new-messages");
						} else {
							hmessage.removeClass("new-messages");
						}      
						
						if (hcount_prev && hcount_prev !== hcount && pblink) {
							hmessage.addClass("blink")
											.delay(10000)
											.queue(function() {
												 $(this).removeClass("blink");
												 $(this).dequeue();
											});
						}
					}
				},
				error: function (pdata){
					clearInterval(message_count_interval);
					alert_isb(pdata.responseText
										+'.<br /><br />Please <a href="javascript:location.reload();">refresh</a> this page.', 'Error', 'error no-close'
										);
				},
				dataType: "xml"
			}
		);
  }
}

function portal_messages() {
  hurl = $v('P0_MESSAGE_URL');
  
  if (Boolean(hurl)) {
    openWindow($url(hurl),'Messages');
  } else {
    var htitle = 'Messages';
    var hhtml = 'No message url has been defined in AE_CUSTOM.GET_MESSAGE_URL.'+
                '<br>Contact ISB.';

    var $dialog = $('<div></div>')
                  .html(hhtml)
                  .dialog({
                            autoOpen    : false,
                            title       : htitle,
                            dialogClass : "PortalDialog error",
                            modal       : true,
                            width       : '400',
                            //height      : '300'
                          });
    $dialog.dialog('open');       
  }
}

function portal_settings() {
  $(".portal-settings").slideToggle('fast');
}

function portal_style(pthis) {
  var pstyle = $(pthis).attr("data-class");
	
	$('#P0_APP_PROC').val('SAVEPORTALSTYLE');
	$('#P0_BODY_CSS').val(pstyle);

	apex.server.process(
		'isb_xml',
		{pageItems: '#P0_APP_PROC'
							+',#P0_BODY_CSS'
		},
		{
			success: function (pdata) {
				var herror = $xml(pdata, "FOUT");
				if (herror){
					alert_isb(herror);
				}
				else{
					//style proberen toepassen op alle schermen
					//we verwijderen classes die beginnen met portal-
					//en plakken dan de nieuwe eraan
					//volledig effect pas na logout en login...
					top.$("body").removeClass(function (index, className) {
																			return (className.match (/(^|\s)portal-\S+/g) || []).join(' ');
																		})
											 .addClass(pstyle);
					top.$(".iframecontent").each(function() {
						try {
							$(this).contents().find("body")
																.removeClass(function (index, className) {
																							 return (className.match (/(^|\s)portal-\S+/g) || []).join(' ');
																						 })
																.addClass(pstyle);
						} catch(err) {
							//indien er een iframe op een ander domein zit krijg je anders een error (blocking)
							console.log(err.message);
						}
					});
				}
			},
			error: function (pdata){
				alert_isb('Unhandled error: '+JSON.stringify(pdata));
			},
			dataType: "xml"
		}
	);
}

function login_remote_auth(premote_auth, pextra_param) {
  //
  //samenstellen van de external NodeJS url
  //ook meegeven van de terugkeer url
  //var hback_url = new URL('./f?p='+App_Id()+':'+page()+':'+session(), window.location.href).href; //new URL werkt niet in IE11
  //var hback_url = rel_to_abs('./f?p='+App_Id()+':'+page()+':'+session()); //rel_to_abs werkt niet correct na verkeerd inloggen ==> apex plakt een soort loginthrottle in de url
  var absolutePath = function(href) {
    var link = document.createElement("a");
    link.href = href;
    return link.href;
  }
  var hback_url = absolutePath('./f?p='+App_Id()+':'+page()+':'+session());
  //
  var hurl = '/node/auth'+premote_auth+'?purl='+encodeURIComponent(hback_url)+'&premote_auth='+premote_auth;
  // 
  if (pextra_param) {
    hurl = hurl+pextra_param;
  }
  //
  if (premote_auth == 'LDAPISB') {
    var husername = $v('P'+page()+'_USERNAME');
    var hpassword = $v('P'+page()+'_PASSWORD');
    //
    if (!husername || !hpassword) {
      //indien niet ingevuld een popup tonen om in te vullen
      $( "<div></div>" )
        .html('<div style="text-align:center">'+
              '<form action="javascript:$(\'#'+premote_auth+'_LOGIN_BUTTON\').trigger(\'click\')">'+ 
              '    <div class="t-Form-inputContainer">'+
              '      <input type="text" id="PORTAL_USERNAME" class="text_field apex-item-text" placeholder="username" value="'+husername+'" >'+
              '    </div>'+
              '    <div class="t-Form-inputContainer">'+
              '      <input type="password" id="PORTAL_PASSWORD" class="text_field apex-item-text" placeholder="password">'+
              '    </div>'+
              '    <input type="submit" hidden />'+
              '  </form>'+
              '</div>'+
              '<br>')
        .dialog({
          title: "Fill in credentials",
          modal: true,
          dialogClass: "PortalDialog info",
          buttons: [{
            text: 'Login',
            id: premote_auth+'_LOGIN_BUTTON',
            click : function() {    
                hurl = hurl+'&username='+$v('PORTAL_USERNAME')+'&password='+$v('PORTAL_PASSWORD');
                window.open(hurl, '_self');
                //
                $(this).dialog("destroy");
              }
            }]
        });        

    } else {
      //indien wel ingevuld
      hurl = hurl+'&username='+husername+'&password='+hpassword;
      window.open(hurl, '_self');  
    }
  } else if (premote_auth == 'TFA') {
    //authTFA gaat over registratie en wordt in apex afgehandeld
    if (typeof authTFA == 'function') {
      authTFA();
    }
  } else {
    window.open(hurl, '_self');  
  }
}

//
//begin: service worker en "Add to home screen"
var installPromptEvent; 
var swRegistration = null;
function serviceWorker() {
  //attach the service worker
  if ('serviceWorker' in navigator) {
    //console.log('Service Worker and Push is supported');
    //
    navigator.serviceWorker.register('/i/isb/alg/js/serviceWorkers/portal_isb_pwa.js?v=1.4', { scope: "/" })
      .then(function(swReg) {
        //console.log('Service Worker is registered', swReg);                
        swRegistration = swReg;
        //html5 notification subscription
        //als de functie bestaat, dan aanroepen
        //zie pagina om te subscriben
        if (typeof initialiseSubscriptionUI == 'function') {
          initialiseSubscriptionUI();
        }
      })
      .catch(function(error) {
        console.error('Service Worker Error', error);
      });
  } else {
    //console.warn('Push messaging is not supported');
  }     
}
window.addEventListener('beforeinstallprompt', function(event) {
  //Prevent Chrome <= 67 from automatically showing the prompt
  event.preventDefault();
  //Stash the event so it can be triggered later. 
  installPromptEvent = event;
  //Update the install UI to notify the user that app can be installed
  hinstallButton = $("#portal-install-app");
  if (hinstallButton.length != 0) {
    hinstallButton.show();
    hinstallButton.on('click.portal', function() {portalInstallApp(this)});
    if (!hinstallButton.html()) {
      //indien geen tekst vullen we hem op
      hinstallButton.html('Install '+document.title+' app');
    }
  }
});   
function portalInstallApp(pthis) {
  //Update the install UI to remove the install button/container
  $("#portal-install-app").hide();
  //Show the modal add to home screen dialog
  installPromptEvent.prompt();
  //Wait for the user to respond to the prompt
  installPromptEvent.userChoice.then(function(choice){
    if (choice.outcome === 'accepted') {
      //console.log('User accepted the A2HS prompt');
    } else {
      //console.log('User dismissed the A2HS prompt');
    }
    //Clear the saved prompt since it can't be used again
    installPromptEvent = null;
  });
}
//einde: service worker en "Add to home screen"

//network status
window.addEventListener('online', function() {
  networkStatusChange('online');
});
window.addEventListener('offline', function() {
  networkStatusChange('offline');
});
var hnetworkStatus;
function networkStatusChange(pstatus) {
  if (!hnetworkStatus) {
    //indien nog niet bestaat, eerst aanmaken
    hnetworkStatus = $('<div id="networkStatus"><div id="networkStatusMsg"></div></div>');
    hnetworkStatus.appendTo('body');
  }
  if (pstatus == 'online') {
    hnetworkStatus.find('div').html('You are back online! <i class="fa fa-emoji-sweet-smile"></i>');
    hnetworkStatus.removeClass('offline').addClass('online').fadeOut('slow');
  } else if (pstatus == 'offline') {
    hnetworkStatus.find('div').html('You have lost connection <i class="fa fa-emoji-frown"></i>');    
    hnetworkStatus.removeClass('online').addClass('offline').fadeIn('slow');
  }
}

//Window,Region and Cookie stuff
var myDate=new Date();
myDate.setFullYear(2076,1,1);

function get_cookies_array() {
  var cookies = { };
  if (document.cookie && document.cookie != '') {
    var split = document.cookie.split(';');
    for (var i = 0; i < split.length; i++) {
      var name_value = split[i].split("=");
      name_value[0] = name_value[0].replace(/^ /, '');
      cookies[decodeURIComponent(name_value[0])] = decodeURIComponent(name_value[1]);
    }
  }
  return cookies;
}

function saveWindow(pwindow) {
  if (pwindow) {
    pwindowcss = '"left":"'+$('.portal-page-float#'+pwindow).css('left')+'"';
    pwindowcss = pwindowcss + ',"top":"'+$('.portal-page-float#'+pwindow).css('top')+'"';
    pwindowcss = pwindowcss + ',"width":"'+$('.portal-page-float#'+pwindow).css('width')+'"';
    pwindowcss = pwindowcss + ',"height":"'+$('.portal-page-float#'+pwindow).css('height')+'"';
    //
    if (html5Storage()) {
      localStorage.setItem('ISBWINDOW_'+$('.portal-page-float#'+pwindow).attr('portal_item'),pwindowcss);
    }
  }
}
function recallWindow(pwindow) {
  if (html5Storage()) {
    for (var i = 0; i < localStorage.length; i++){
      var name = localStorage.key(i);
      if (name.indexOf('ISBWINDOW_')!=-1){
        if ($('.portal-page-float#'+pwindow).attr('portal_item') == name.substring('ISBWINDOW_'.length)) {
          //er is een key voor het doorgegeven pwindow
          var hcss = $.parseJSON('{' + localStorage.getItem(localStorage.key(i)) + '}');
          $('.portal-page-float#'+pwindow).css(hcss);
        }	   
      }
    }
  }
}

/*Taskbar*/
function addToTaskbar(ptaskbarWindowId, pportal_item, ptitle){
  var hfavorite = '';
  if (pportal_item) {
    hfavorite = '<div class="taskbarTaskFavorite" title="add as favorite"></div>';
  }
  
  var htask = $('<div class="taskbarTask" id="task_' + ptaskbarWindowId + '"'+
                    ' title="'+ptitle+'"'+
                    ' data-line="'+ptaskbarWindowId+'">'+
                  ptitle+ 
                  hfavorite+
                  '<div class="taskbarTaskWindowToggle"></div>'+
                  '<div class="taskbarTaskClose"></div>'+
                '</div>'
               );
             
  //events toevoegen
  //taskbarWindowId activeren
  htask.on('click.portal', function (event) { 
    top.activateTaskbar(ptaskbarWindowId);
  });
  //zetten als favorite 
  htask.find(".taskbarTaskFavorite").on('click.portal', function (event) { 
    top.AddFavorite(pportal_item);
  });
  //close window
  htask.find(".taskbarTaskClose").on('click.portal', function (event) { 
    top.closeWindow(ptaskbarWindowId);
  });
  //maximize toggle
  htask.find(".taskbarTaskWindowToggle").on('click.portal', function (event) { 
    //toggle de class "max"
    top.$(".taskbarTask[data-line="+ptaskbarWindowId+"] .taskbarTaskWindowToggle").toggleClass("max");
    //toggle class "maximize" en "normal" op scherm
    top.$(".portal-page-float[id="+ptaskbarWindowId+"]").toggleClass("maximize normal");
  });
    
  htask.appendTo('.portal-taskbar .portal-taskbar-inner');
  
  activateTaskbar(ptaskbarWindowId);
}

function deleteFromTaskbar(pid){
  pdelete = '[id=task_'+ pid+']';
  $(pdelete).empty().remove();
  //
  taskbarButton();
}

function activateTaskbar(pid){
  $('.taskbarTask').removeClass('active');
  $('[id=task_'+ pid+']').addClass('active');
  //
  $('.portal-page-float').removeClass('active');
  $('.portal-page-float#'+pid).addClass('active');
  $('.portal-page-float#'+pid).css({'z-index' : maxZ(".portal-page-float")});
  
  //toon extra knop
  taskbarButton();
  
  //scroll taskbar
  var hleft, hnewLeft, hwidthOfTaskbar, hwidthOfButton, htaskbarTask, htaskbarTaskLeft, htaskbarTaskRight;
  
  hleft = $("#portal-header .portal-taskbar-inner").position().left;
  hwidthOfTaskbar = $("#portal-header .portal-taskbar").outerWidth();
  hwidthOfButton = $("#portal-header .portal-taskbar-left").outerWidth();
  htaskbarTask = $("#portal-header #task_"+pid);
  htaskbarTaskLeft = hleft + htaskbarTask.position().left;
  htaskbarTaskRight = htaskbarTaskLeft + htaskbarTask.outerWidth();
  
  //
  if ( htaskbarTaskRight > (hwidthOfTaskbar - hwidthOfButton) ) {
    //verschuiven naar rechts
    hnewLeft = (hwidthOfTaskbar - hwidthOfButton) - htaskbarTaskRight + hleft;
  }
  if ( htaskbarTaskLeft < hwidthOfButton ) {
    //verschuiven naar rechts
    hnewLeft = hwidthOfButton - htaskbarTaskLeft + hleft;
  }
  
  //scrollen
  if (hnewLeft) {
    $("#portal-header .portal-taskbar-inner").finish().animate({left:hnewLeft+"px"},'400',function(){ });  
  }
}

function taskbarButton() {
  if ($(".taskbarTask").length != 0) {
    $(".taskbarButton").show();    
    $("#portal-header .favorite").hide();
  } else {
    $(".taskbarButton").hide();
    $("#portal-container>.portal-taskbar").slideUp();
    $("#portal-header .favorite").show();
  }
}

function toggleTaskbar() {
  $("#portal-container>.portal-taskbar").slideToggle();
  $("#portal-header .taskbarButton").toggleClass("fa-rotate-180");
}

function taskbarMove(hbutton){
  //https://codepen.io/srees/pen/pgVLbm
  var hleft, hnewLeft, hwidthOfTaskbar, hwidthOfTasks, hwidthOfButton;
  
  hleft = $("#portal-header .portal-taskbar-inner").position().left;
  hwidthOfTaskbar = $("#portal-header .portal-taskbar").outerWidth();
  hwidthOfTasks = 0;
  $("#portal-header .portal-taskbar-inner .taskbarTask").each(function(){
    hwidthOfTasks += $(this).outerWidth();
  });  
  hwidthOfButton = $("#portal-header .portal-taskbar-left").outerWidth();
  
  if (hbutton == 'L') {
    //linkse button: meer rechts tonen
    hnewLeft = hleft + (hwidthOfTaskbar/2);
  } else {
    //rechtse button: meer links tonen
    hnewLeft = hleft - (hwidthOfTaskbar/2);
  }
  
  //controles
  if ( hnewLeft < (hwidthOfTaskbar - hwidthOfTasks - hwidthOfButton) ) {
    //niet te ver naar links verschuiven
    hnewLeft = (hwidthOfTaskbar - hwidthOfTasks - hwidthOfButton);
  }
  if ( hnewLeft > hwidthOfButton ) {
    //niet te ver naar rechts verschuiven
    hnewLeft = hwidthOfButton;
  }
  
  //scrollen
  $("#portal-header .portal-taskbar-inner").finish().animate({left:hnewLeft+"px"},'400',function(){ });  
}
