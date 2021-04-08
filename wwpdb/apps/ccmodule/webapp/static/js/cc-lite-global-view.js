/**************************************************************************************************************
File:		cc-lite-global-view.js
Author:		rsala (rsala@rcsb.rutgers.edu)

JavaScript supporting Ligand Lite Module web interface 

2011-12-08, RPS: This file created to house code for managing "global view" and which originally from ligmod.js
2013-04-02, RPS: Added tracking of ligand groups for which mismatches are addressed by depositor.
2013-09-16, RPS: Updated handling of "filesource" identifier on Save, Finish actions.
2013-10-15, RPS: First accordion level now expanded by default.
2013-12-13, RPS: Modified handling of calls to generate-and-check-for ligand match results, to allow successful
					processing in Chrome and Internet Explorer.
2013-12-16, RPS: checkForRsltsData() using "false" for ajax "cache" option in order to have this work properly
					 in IE which otherwise caches ajax requests if "GET" used.
2014-01-21, RPS: Changes in behavior/display/placement of buttons handling entry/exit from module and navigation within the module.
					Augmented help text provisions.
2014-01-22, RPS: Preventing premature activation of navigation buttons.
					Updated to provide navigation buttons at bottom of screen in instance level view
2014-01-23, RPS: Scrolling to top of pane with clicks of "Back to Summary View" button.
2014-01-24, RPS: Moved activation of jPaginate back to proper place instead of in applyBeautyTips()
2014-02-03, RPS: Updated with check for and display of confirmation for already uploaded component-definition files.
2014-03-11, RPS: Preventing duplicate alert dialogs on click of Finish button.
2014-03-19, RPS: Instituted workaround to allow handling of URL references with custom prefixes.
2014-05-09, RPS: Fix for absence of "indexOf" function in IE8 and lower
2014-06-23, RPS: Updates in support of providing more elaborate choices for choosing an alternate Ligand ID
 				 (originally proposed ID vs. one of the possible exact match IDs for cases where some ligand instances have 
 				 differing matches).
2014-10-31, RPS: Providing 2D image of author proposed Ligand ID in "handle mismatch" section, on hover over of the ID.
2015-10-15, RPS: "startsWith" String.prototype function definition removed as it conflicted with similar strategy used by jsmol. 
2016-03-03, RPS: Addressed bug that had arisen affecting use of BeautyTips to provide pop-up image of auth assigned ID and exact match ID 
2016-04-13, RPS: Updated to remove all AJAX calls where async option was set to 'false'. 
2017-02-03, RPS: Updated to support capture of data for ligands as "focus of research"
2017-02-07, RPS: Improved handling of validation for data input for ligands as "focus of research".
					Fix for issue with tracking those IDs chosen for viewing in instance browser.
					Updated with help text and tooltips.
2017-02-08, RPS: Updates for button labels and tooltip behavior.
					Added feature for copying descriptor string from address mismatch section to binding assay section.
2017-02-09, RPS: Fixing glitches in checkbox behavior.
2017-02-14, RPS: Updates for UI controls behavior and input validation checking.
2017-02-15, RPS: Removing "Save (and come back later) button which has become obsolete.
2017-02-16, RPS: Updates to accommodate additional validation requirements.
2017-02-17, RPS: Improving behavior and labels of controls for capturing research data.
2017-02-20, RPS: Fixed bug with saving descriptor string that has been copied from ligand verification section to research section.
2017-03-27, RPS: Disabling recent updates for capturing HOH research of interest data.
****************************************************************************************************************/
var DEVTEST = false;

if(!Array.prototype.indexOf){
	Array.prototype.indexOf = function(obj, start) {
	     for (var i = (start || 0), j = this.length; i < j; i++) {
	         if (this[i] === obj) { return i; }
	     }
	     return -1;
	}
}

if(!String.prototype.replaceAll){
	String.prototype.replaceAll = function(srchStr, rplcmntStr){
		var inputStr = this;
		return inputStr.replace(new RegExp(srchStr, 'g'), rplcmntStr)
	};
}

///////////////////// FUNCTION DEFINITIONS - Global Ligand Summary View ///////////////////////////////////////////
$(document).on('lazybeforeunveil', function (e) {
	var target = $(e.target);

	if (!target) {
		return;
	}

	if (target.attr('id') === 'mismatch_section') {
		var ajax = target.data('ajax');

		if (ajax) {
			target.load(ajax);
		}

		return;
	}

	if (!target.hasClass('single_instance')) {
		// then it's the header, we must expand it
		target.next().show('slow');
		target.find('span.ui-icon').toggleClass('ui-icon-circle-arrow-s ui-icon-circle-arrow-e');
	} else {
		var ajax = target.data('ajax');

		if (ajax) {
			target.load(ajax);
		}
	}
});

function renderHtmlTemplate(response, targetElement) {
	var numberText = ["Zero","One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight","Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
		"Sixteen", "Seventeen", "Eighteen", "Nineteen","Twenty"];

	templateData = {
		depId: CC_LITE_SESSION_DATA.depId,
		getReportFileServiceUrl: CC_LITE_SESSION_DATA.servicePathPrefix + ChemCompLiteMod.URL.GET_REPORT_FILE,
		ligands: [],
	};

	rKeys = Object.keys(response);
	tabStyle = '_current';

	for (var i = 0; i < rKeys.length; i++) {
		if (i + 1 > 1) {
			tabStyle = 'displaynone';
		}

		ligGroupData = response[rKeys[i]];

		ligandEntry = {
			index: i + 1,
			tabStyle: tabStyle,
			ligGroup: rKeys[i],
			dynamicText: {},
			data: ligGroupData,
		};
		
		// mismatch text
		if (ligGroupData['bGrpRequiresAttention']) {
			var text1 = ligGroupData['totlInstncsInGrp'] > 1 ? 'there is at least one instance for which ' : '';
			var text2 = ligGroupData['totlInstncsInGrp'] > 1 ? 'sections below for those instances that require ' : 'section below for the instance that requires ';

			ligandEntry.dynamicText.mismatchMessage = '<br /><br />However, ' + text1 + 'there is a discrepancy between the coordinates for ' + rKeys[i] + ' and the possible match in the CCD. Please see ' + text2 + 'attention. Clicking on section headers labelled "instance" will expand/collapse content. Both 2D and 3D comparison views are provided.<br /><br />The section "address mismatched instances of: ' + rKeys[i] + '" allows you to provide more information about this ligand. Please provide at least one of the following: an alternative ligand ID, a chemical diagram by file upload of image file or a descriptor string in SMILES/InChI format. When you have finished with this ligand, press the "Save" button at the bottom of the page.';
		} else {
			ligandEntry.dynamicText.mismatchMessage = '';
		}

		// singular/plurar variants
		ligandEntry.dynamicText.have = ligGroupData['totlInstncsInGrp'] > 1 ? 'have' : 'has';
		ligandEntry.dynamicText.copy = ligGroupData['totlInstncsInGrp'] > 1 ? 'copies' : 'copy';
		ligandEntry.dynamicText.totalText = ligGroupData['totlInstncsInGrp'] > 21 ? ligGroupData['totlInstncsInGrp'] : numberText[ligGroupData['totlInstncsInGrp']];
		
		// css classes
		ligandEntry.data.bGrpRequiresAttention = ligandEntry.data.bGrpRequiresAttention ? 'attn_reqd' : '';
		ligandEntry.data.bGrpRequiresAttentionDisplay = ligandEntry.data.bGrpRequiresAttention ? '' : 'displaynone';
		ligandEntry.data.isResolvedClass = ligandEntry.data.isResolved ? 'is_rslvd' : 'not_rslvd';

		if (ligandEntry.data.bGrpRequiresAttention === 'attn_reqd') {
			ligandEntry.mismatchUrl = CC_LITE_SESSION_DATA.servicePathPrefix + ChemCompLiteMod.URL.GET_REPORT_FILE + '?identifier=' + CC_LITE_SESSION_DATA.depId + '&source=report&ligid=' + ligandEntry.ligGroup + '&file=' + ligandEntry.ligGroup + '_mismatch.html';
		} else {
			ligandEntry.mismatchUrl = null;
		}

		templateData.ligands.push(ligandEntry);
	}

	return fetch('/ccmodule_lite/templates/workflow_ui/instances_view/cc_instance_browser_template.html')
    .then(function (response) { return response.text() })
    .then(function (template) {
      var rendered = Mustache.render(template, templateData);
			document.getElementById(targetElement).innerHTML = rendered;
    });
}

function applyBeautyTips() {
	/***$('#help_instnc_brwser_vw').bt({positions: ['left', 'bottom'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule/cc_help.html div#instance',ajaxOpts:{dataType:'html'},trigger: 'click',
	width: 600,centerPointX: 0.9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
	strokeStyle: '#ABABAB',strokeWidth: 1});***/
	jQuery.bt.options.cssStyles = {font: '12px sans-serif', fontFamily: 'Verdana,Arial,sans-serif'};
	
	$('.save_descr').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#save_btn',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: 0.9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.save_rsrch_data').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#save_rsrch_btn',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: 0.9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.save_exact_mtch_id').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#save_btn',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: 0.9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('div.savedone').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#finish',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.instance_browser_ui').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#instnc_srch_scrn',ajaxOpts:{dataType:'html'},trigger: 'hover',
	width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
	strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.back_to_summary_vw').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#lgnd_summry_scrn',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('span.tophit').bt({positions: ['bottom','left','top'],contentSelector: "$('#twoD_'+$(this).text()+'')",trigger: 'hover',
		centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('span.author_assgnd_id').bt({positions: ['bottom','left','top'],contentSelector: "$('#'+$(this).text()+'_2d_auth_assgnd')",trigger: 'hover', 
		centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1, ajaxError: "There was a problem getting this content. Ligand ID may be invalid."});
	$('textarea.capture_rsrch_data_input.target_seq').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#binding_target_seq',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('select.capture_rsrch_data_input.dscrptr_type').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_dscrptr_str',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('input.capture_rsrch_data_input.rsrch_dscrptr_str').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_dscrptr_str',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('input.capture_rsrch_data_input.ph').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_ph',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('input.capture_rsrch_data_input.temp').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_temp',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('select.capture_rsrch_data_input.measurement_type').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_measurement_type',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('input.capture_rsrch_data_input.measured_value').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_measured_value',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('textarea.capture_rsrch_data_input.details').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_details',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.target_sequence_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#binding_target_seq',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.rsrch_dscrptr_type_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_dscrptr_str',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	/**$('.rsrch_dscrptr_str_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_dscrptr_str',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});**/
	$('.ph_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_ph',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.assay_temp_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_temp',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.measurement_type_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_measurement_type',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.measured_value_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_measured_value',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.details_lbl').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_details',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.head.rsrch_data').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#rsrch_hdr',ajaxOpts:{dataType:'html'},
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF', trigger: 'hoverIntent', hoverIntentOpts: {interval: 150},
		strokeStyle: '#ABABAB',strokeWidth: 1});
	
}

function closeWindow() {
    //uncomment to open a new window and close this parent window without warning
    //var newwin=window.open("popUp.htm",'popup','');
    if(navigator.appName=="Microsoft Internet Explorer"){
        this.focus();self.opener = this;self.close(); 
    } else {
            window.open('','_parent',''); window.close(); 
    }
}
function unresolvedGrpsHandler() {
	var numToResolve = 0;
   	$('#rslts td.resolve_status').each( function() {
		var rslvstatus = $(this).html();
		if( rslvstatus == 'Mismatch(es) Require Attention'){
			numToResolve = numToResolve + 1;
			$(this).removeClass('beenrslved');
		}
		else{
			if( rslvstatus != 'OK' ){
				$(this).addClass('beenrslved');
			}
		}
	});
   	/**
   	if( numToResolve === 0 ){
   		$(".savedone").removeAttr('disabled');
   	}
   	else if ( numToResolve > 0 ){
   		$(".savedone").attr('disabled','disabled');
   	}**/
   	return numToResolve;
}

function getBrowserType() {
	$.browser.firefox = /firefox/.test(navigator.userAgent.toLowerCase());
	$.browser.chrome = /chrom(e|ium)/.test(navigator.userAgent.toLowerCase());
	$.browser.msie = /trident/.test(navigator.userAgent.toLowerCase());
	//alert("userAgent: "+navigator.userAgent);
	if($.browser.chrome){
		//alert("Chrome Browser detected. userAgent: ("+navigator.userAgent+")");
		ChemCompLiteMod.currBrowser = "chrome";
	}
	if($.browser.firefox){
		//alert("Firefox Browser detected. userAgent: ("+navigator.userAgent+")");
		ChemCompLiteMod.currBrowser = "firefox";
	}
	if($.browser.msie){
		//alert("MSIE Browser detected. userAgent: ("+navigator.userAgent+")");
		ChemCompLiteMod.currBrowser = "msie";
	}
}
function getLigSummaryRslts() {
	//getBrowserType();
	//alert("in getLigSummaryRslts()");
	$(ChemCompLiteMod.loadSmmryFrmLctr).ajaxSubmit({url: ChemCompLiteMod.URL.GEN_LIG_SMMRY_RSLTS, async: true, clearForm: false,
        success: function(jsonOBJ) {
			checkSummaryStatus(jsonOBJ, ChemCompLiteMod.URL.CHECK_FOR_SMMRY_DATA);
        }
    });
    return false;
}

function checkSummaryStatus(jsonOBJ, checkForDataURL) {
	try {
		var delaySecsServer = 3; //delay interval used by server side process
		/**
		 if( ChemCompLiteMod.currBrowser == "chrome" ){
			delaySecsServer = 3;
		}
		*/
		var delayMilliSecsBrowser = 3000; //delay interval enforced by browser here via javascript
		
		ChemCompLiteMod.dataAvail = "no";
		
		var pollingSrvc=setInterval(function(){pollingFunc(jsonOBJ,checkForDataURL,delaySecsServer);},delayMilliSecsBrowser);
		
		function pollingFunc(jsonOBJ,checkForDataURL,delaySecsServer){
			checkForRsltsData(jsonOBJ,checkForDataURL,delaySecsServer);
			if( ChemCompLiteMod.dataAvail == "yes" ){
				stopPollSrvc();
			}
		}
		
		function stopPollSrvc(){
			clearInterval(pollingSrvc);
			$(ChemCompLiteMod.loadSmmryFrmLctr).ajaxSubmit({url: ChemCompLiteMod.URL.LOAD_LIG_SMMRY_DATA, async: true, clearForm: false,
				target: '#rslts',
	        	success: function() {
					$(".savedone").removeAttr('disabled');
	            	applyBeautyTips();
	            	unresolvedGrpsHandler();
								updateSummarySelect();
	            	$(".instance_browser_ui").removeAttr('disabled');
				},
				error: function() {
					$('.errmsg').html(errStyle + 'Failed to load ligand summary data.' + '<br />\n' + ChemCompLiteMod.adminContact).show();
				}
			});
			return false;
		}
		
	} catch(err) {
		//$('.errmsg').html(errStyle + 'Error: ' + JSON.stringify(jsonOBJ) + '<br />\n' + ChemCompLiteMod.adminContact).show().delay(5000).slideUp(800);
		$('.errmsg').html(errStyle + 'Error on checking for ligand summary data.<br />\n' + ChemCompLiteMod.adminContact).show().delay(5000).slideUp(800);
	}
}

function loadSummaryData() {
	$(ChemCompLiteMod.loadSmmryFrmLctr).ajaxSubmit({url: ChemCompLiteMod.URL.LOAD_LIG_SMMRY_DATA, async: true, clearForm: false,
		target: '#rslts',
				success: function() {
			$(".savedone").removeAttr('disabled');
						applyBeautyTips();
						unresolvedGrpsHandler();
						updateSummarySelect();
						$(".instance_browser_ui").removeAttr('disabled');
		},
		error: function() {
			$('.errmsg').html(errStyle + 'Failed to load ligand summary data.' + '<br />\n' + ChemCompLiteMod.adminContact).show();
		}
	});
}

function updateSummarySelect(){
    // Update the display of the selection boxes
    // Returns true if at least one LOI has been selected
    // backgroundColor needs to be ued due to jquery 1.4 in DepUI
    if ($('.selectinstnc_td :checked').length > 0) {
	// Set to transparent maybe?
	$(".selectinstnc_td").css("backgroundColor", "");
	if ($('.c_NONE_special .selectinstnc_td :checked').length > 0) {
	    // NONE is selected
	    $('#ligand_inventory_tbl .selectinstnc_td .selectinst_stdgrp').attr('disabled', 'disabled');
	    $('#ligand_inventory_tbl .selectinstnc_td .selectinst_none').removeAttr('disabled');
	} else {
	    // NONE is not selected
	    $('#ligand_inventory_tbl .selectinstnc_td .selectinst_stdgrp').removeAttr('disabled');
	    protectRsrchDataHandler()
	    $('#ligand_inventory_tbl .selectinstnc_td .selectinst_none').attr('disabled', 'disabled')
	}

    } else {
	// Nothing selected - all get enabled - unless restricted
	$(".selectinstnc_td").css("backgroundColor", "#FFE6E6");
	$('#ligand_inventory_tbl .selectinstnc_td .selectinst_stdgrp').removeAttr('disabled');
	protectRsrchDataHandler()
	$('#ligand_inventory_tbl .selectinstnc_td .selectinst_none').removeAttr('disabled');
    }

}


function checkForRsltsData(jsonOBJ,checkForDataURL,delaySecsServer){
	//if( ChemCompLiteMod.currBrowser == "msie" ){
		//alert("called check for results data.");
	//}
	var returnCode;
	$.ajax({type: 'GET',url: checkForDataURL, async: true, cache: false, data: {'semaphore': jsonOBJ.semaphore,'sessionid': CC_LITE_SESSION_DATA.sessionID,'delay': delaySecsServer},
		success: function(resOBJ) {
			returnCode = resOBJ.statuscode;
			if( returnCode == 'completed' ){
				ChemCompLiteMod.dataAvail = "yes";
			}
		},
		error: function(resOBJ) {
			alert("error on call to check for results data");
		}
	});
	return returnCode;
}

function checkMissingLigandTypeField(ccid){
	var bMissingReqdField= false;
	
	if (!$("#lgnd_type_"+ccid+" input[name='lgnd_type']:checked").val()) {
		bMissingReqdField = true;
	}
	
	if(!bMissingReqdField){
		$('#fieldset_lgnd_type_'+ccid).css({ 'border-color':'#f6f6f5', 'background-color':'#FFF', 'border-style': 'groove', 'border-width': '2px' });
	}else{
		$('#fieldset_lgnd_type_'+ccid).css({ 'border-color':'#CD0A0A', 'background-color':'#FEF1EC', 'border-style': 'solid', 'border-width': '1px' });
	}
	
	return bMissingReqdField;
}

function loadInstanceBrowserView() {
	ChemCompLiteMod.activeCCid = 1;
	$('#ligand_summary_vw').hide();
	$('#help_batch_smmry_vw').hide();
	//$('#instnc_brwser_vw').show();
	//alert('length of instnc section: '+$('#instnc_browser_container').html().length);
	
	// LIST OF MISMATCHED VS. RSLVD LIGIDS WILL NEVER INCLUDE H2O /////////////////////
	
	var listOfMismatchedLigIds = $('#mismatchlist').html();
	ChemCompLiteMod.ligIdsMismatched = listOfMismatchedLigIds.split(",");
	var listOfResolvedLigIds = $('#rslvdlist').html();
	if( listOfResolvedLigIds ){
		ChemCompLiteMod.ligIdsRslvd = listOfResolvedLigIds.split(",");
	}
	var listOfLigIds = $('#ligids').val(); // i.e. currently selected in global view
	var listOfLigIdsForInstVw = $('#ligids_inst_vw').val(); // i.e. last known list of those IDs which were inpsected in Instance Browser view
	var listOfLigIdsRsrchFocus = $('#ligids_rsrch').val(); // i.e. currently selected in global view
	var listOfLigIdsRsrchForInstVw = $('#ligids_rsrch_inst_vw').val(); // i.e. last known list of those IDs which were inpsected in Instance Browser view
	if( $('#instnc_browser_container').html().length <= 150 || ( listOfLigIdsForInstVw != listOfLigIds ) || ( listOfLigIdsRsrchForInstVw != listOfLigIdsRsrchFocus ) ){
		$('#instnc_browser_container').html('<div class="loading_msg">&nbsp;&nbsp;<img src="/images/loading.gif" alt="loading..." />&nbsp;&nbsp;Data being processed.</div>');
		$('#instnc_brwser_vw').show();
		$('#ligids_inst_vw').val(listOfLigIds);
		$('#ligids_rsrch_inst_vw').val(listOfLigIdsRsrchFocus);
		
		$('#inst_brwsr_frm').ajaxSubmit({url: CC_LITE_SESSION_DATA.servicePathPrefix + ChemCompLiteMod.URL.GET_LIGAND_SUMMARY, async: true, clearForm: false,
    		beforeSubmit: function (formData, jqForm, options) { formData.push({"name": "browser", "value": ChemCompLiteMod.currBrowser }); },
					target: '#instnc_browser_container',
					success: function(response) {

					renderHtmlTemplate(response, 'instnc_browser_container').then(function () {
						$('#pagi').paginate({count: $('.tabscount').size(), start:ChemCompLiteMod.activeCCid, display:6, border:true, border_color:'#BEF8B8',
						text_color:'#68BA64', background_color:'#E3F2E1', border_hover_color:'#68BA64', text_hover_color:'black',
						background_hover_color:'#CAE6C6', images:false, mouse:'press', onChange: function(page){
								$('._current').removeClass('_current').slideUp('slow');
								$('#p'+page).addClass('_current').slideDown('slow');
								$('#p_'+page).addClass('_current').slideDown('slow');
								$('#p__'+page).addClass('_current').slideDown('slow');
								ChemCompLiteMod.activeCCid = page;
							}
						});

						$('.single_instance').hide();

						//have to do below because content is usually loaded on click of component navigation browser
						//but on first load of page, the content below should be shown by default (i.e. without requiring user clicks)
						var firstGrp = $('.cmpnt_grp:first').html();
						//First accordion level now expanded by default with below

						$('.inneraccordion').each( function(index) {
							$(this).find('.single_instance:first').show();
							$(this).find('span.ui-icon:first').toggleClass('ui-icon-circle-arrow-s ui-icon-circle-arrow-e');
						});

						//Address mismatches level now expanded by default with below
						$('.inneraccordion div.all_instances').each( function(index) {
							$(this).show();
							$(this).parent().find('a.all_instances span.ui-icon').toggleClass('ui-icon-circle-arrow-s ui-icon-circle-arrow-e');
							var ligId = $(this).attr('name');
							checkMissingLigandTypeField(ligId);
							checkForUploadedImageFiles(ligId, "requirementscheck");
							//checkMissingAssrtdReqdFields(ligId);
							checkCompDefFileUploads(ligId,"refresh");
						});

						$('#restart').click(function() {
								alert("[PLACEHOLDER] -- will perform restart action");
							});

						$(".savedone").removeAttr('disabled');
						$(".instance_browser_ui").removeAttr('disabled');
						$('.back_to_summary_vw').removeAttr('disabled');
						$('.back_to_summary_vw').show();
						$(".instance_browser_ui").hide();
						
						$(document).on('click','.back_to_summary_vw', function() {
							window.parent.$("div.ui-layout-center.ui-layout-pane.ui-layout-pane-center").animate({scrollTop:0}, 'slow');
								$('.back_to_summary_vw').hide();
								$(".instance_browser_ui").show();
								$("#instnc_brwser_vw").hide();
								$('#help_instnc_brwser_vw').hide();
								unresolvedGrpsHandler();
								$("#ligand_summary_vw").show();
								$("#help_batch_smmry_vw").show();
								
								protectRsrchDataHandler();
						});

						applyBeautyTips();
						/*
						$('#help').click(function() {
											alert("[PLACEHOLDER]");
							});
							*/
							disableCopyRsrchDscrptr();
					});
        }
      });

    	$('ul.jPag-pages li').each( function(index) {
				var ligId = $(this).text();

				if( ChemCompLiteMod.ligIdsMismatched.indexOf(ligId) >= 0){
					$(this).addClass("attn_reqd");
				}

				if( ChemCompLiteMod.ligIdsRslvd && ChemCompLiteMod.ligIdsRslvd.indexOf(ligId) >= 0){
					$(this).addClass("is_rslvd");
					$(this).removeClass("attn_reqd");
				}
    	});
      
			return false;
	}
	else{
		$('#instnc_brwser_vw').show();
		$('.back_to_summary_vw').show();
    	$(".instance_browser_ui").hide();
	}
}

function disableCopyRsrchDscrptr(){
	// disable button that copies descrptor string from Ligand Verification section to Research data capture section
	$('.copy_rsrch_dscrptr_str').each( function(index) {
    	//disable the "copy dscrptr" button for ligands without Ligand Verification section
    	var elemId = $(this).attr("id");
		var splitArr = elemId.split("_");
		var authAssgnGrp = splitArr[5];
		
		if( (ChemCompLiteMod.ligIdsMismatched && ChemCompLiteMod.ligIdsMismatched.indexOf(authAssgnGrp) < 0) && ( ChemCompLiteMod.ligIdsRslvd && ChemCompLiteMod.ligIdsRslvd.indexOf(authAssgnGrp) < 0) ){
			$(this).attr('disabled','disabled');
		}
		
	});
}

function protectRsrchDataHandler(){
	for (var i = 0; i < ChemCompLiteMod.ligIdsWithRsrchSubmitted.length; i++) {
        var ligId = ChemCompLiteMod.ligIdsWithRsrchSubmitted[i];
        $("#"+ligId+"_rsrch").attr('disabled','disabled');
    }
	
	for (var i = 0; i < ChemCompLiteMod.ligIdsMissingRsrch.length; i++) {
        var ligId = ChemCompLiteMod.ligIdsMissingRsrch[i];
        $("#"+ligId+"_rsrch").removeAttr('disabled');
    }
     
}

function disableRsrchDataCntrls(ligid,mode) {
	$('.capture_rsrch_data_input.c_'+ligid).each(function() {
		$(this).attr('disabled','disabled');
	});
	revertColorRsrchDataSaveBtn(ligid);
	
}

function enableRsrchDataCntrls(ligid,mode) {
	$('.capture_rsrch_data_input.c_'+ligid).each(function() {
		$(this).removeAttr('disabled');
	});
	disableCopyRsrchDscrptr();
	
}


function checkForValidInput(input,inputType,mode){
	var validVal = false;
	
	if( input && input.length > 0 ){
		validVal = input.trim().match(ChemCompLiteMod.inputTypeValidation[inputType]);
	}
	
	if(!validVal && mode === "notify"){
		alert("Invalid "+ChemCompLiteMod.inputTypeValidation.displaytext[inputType]+" entered. Please correct.");
	}
	
	return validVal;
}

function enableRsrchDataSaveBtn(authAssgnGrp){
	$(".capture_rsrch_data_submit_"+authAssgnGrp).removeAttr('disabled');
	highlightColorRsrchDataSaveBtn(authAssgnGrp);
}

function revertColorRsrchDataSaveBtn(authAssgnGrp){
	$(".capture_rsrch_data_submit_"+authAssgnGrp).css('color','');
}

function highlightColorRsrchDataSaveBtn(authAssgnGrp){
	$(".capture_rsrch_data_submit_"+authAssgnGrp).css('color','red');
}
///////////////////// END OF FUNCTION DEFINITIONS - Global Ligand Summary View /////////////////////////////////////////

//////////////////// FUNCTION CALLS - Global Ligand Summary View //////////////////////////////////////////////////////
// getBrowserType();
// getLigSummaryRslts();

function getAnalysisState() {
	return fetch(ChemCompLiteMod.URL.GET_REPORT_STATUS + '?sessionid=' + CC_LITE_SESSION_DATA.sessionID + '&identifier=' + CC_LITE_SESSION_DATA.depId + '&instance=&filesource=deposit')
		.then(function (r) { return r.json() })
		.then(function (r) {
			switch (r.state) {
				case 'running':
					$('.loading_msg').get(0).innerText = 'Analysis still in progress... ' + Number.parseFloat(r.progress*100).toFixed(2) + '% complete.';
					break;
				case 'finished':
					clearInterval(window.stateHandle);
					loadSummaryData();
					break;
				case 'missing_file':
					$('.loading_msg').get(0).innerText = 'Running pre-analysis operations. This may take a while.';
					break;
				case 'stopped':
				case 'unknown':
					clearInterval(window.stateHandle);
					$('.loading_msg').get(0).innerHtml = 'Something went wrong. Please, run the analysis again.';
					break;
				default:
					break;
			}

			return r;
		});
}

getAnalysisState()
	.then(function (r) {
		if (r.state == 'running') {
			window.stateHandle = setInterval(getAnalysisState, 3000);
		}
	});

//////////////////// END OF FUNCTION CALLS - Global Ligand Summary View ///////////////////////////////////////////////

//////////////////// EVENT HANDLERS - Global Ligand Summary View //////////////////////////////////////////////////////
$(document).on('click','input.savedone', function() {
	var numToResolve = 0;
	var fsrc = CC_LITE_SESSION_DATA.fileSource.toLowerCase();
	if( fsrc == "deposit" ){
		$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.EXIT_FINISHED, clearForm: false,
            beforeSubmit: function (formData, jqForm, options) {
            	numToResolve = unresolvedGrpsHandler();
		var loidone = $('.selectinstnc_td :checked').length > 0;
        	    if( numToResolve > 0 ){
        	    	alert("Ligand processing cannot be completed because one or more ligands require attention. Please address any outstanding mismatches.");
        	    	return false;
        	    }
        	    if( !loidone ){
			if ($(".instance_browser_ui").is(":visible")) {
        	    	    alert("Ligand processing cannot be completed as 'Focus of Research' has not been specified from this page.");
			} else {
        	    	    alert("Ligand processing cannot be completed as 'Focus of Research' has not been specified from summary page. Please press the 'Back to Summary View' button to return to summary page to correct this.");
			    }
        	    	return false;
        	    }
        	    formData.push({"name": "sessionid", "value": CC_LITE_SESSION_DATA.sessionID});
            }, success: function() {
				alert("Work will be saved and ligand processing now complete.");
                if( DEVTEST ){
                	$('html').html('TESTING: you can inspect result files/uploads <a href="'+CC_LITE_SESSION_DATA.servicePathPrefix+'/sessions/'+CC_LITE_SESSION_DATA.sessionID+'/results.html">here</a>');
                }else{
                	closeWindow();
                	$('html').html('');
                }
            }
        });
	}
	else{
   		numToResolve = unresolvedGrpsHandler();
	    if( numToResolve > 0 ){
	    	alert("Ligand processing cannot be completed because one or more ligands require attention. Please address any outstanding mismatches.");
	    	return false;
	    }
    	alert("Save (Done)");
		checkval=0;
    	closeWindow();
        $('html').html('')
	}
});

$(document).on('click','.instance_browser_ui', function() {
	var thisLigID;
	var thisLigIdRsrch;
	var ligIds = '';
	var ligIdsRsrch = '';
	var ligCount = 0;
    $('#ligand_summary_vw :checkbox:checked:not(#selectall):not(.selectinstnc_rsrch):not(#selectall_rsrch)').each(function() {
    	thisLigID = $(this).attr('name');
    	ligIds += ((ligIds.length > 0) ? ',' : '') + thisLigID;
    	if( ChemCompLiteMod.ligIdsSlctdForInstcVw.indexOf(thisLigID) < 0 ){
    		ChemCompLiteMod.ligIdsSlctdForInstcVw.push(thisLigID); //RPS, 20121130: planning to use this for smarter re-rendering of instance browser    		
    	}
    	//alert("Captured value of 'name' for viewing in instance browser: " + $(this).attr('name') );
		
    });
    $('#ligand_summary_vw :checkbox:checked:not(#selectall):not(.selectinstnc):not(#selectall_rsrch)').each(function() {
    	thisLigIdRsrch = $(this).attr('name').split("_")[0];
    	ligIdsRsrch += ((ligIdsRsrch.length > 0) ? ',' : '') + thisLigIdRsrch;    	
		
    });
    $('#ligids').val(ligIds);
    $('#ligids_rsrch').val(ligIdsRsrch);
	//alert("Value of ligIds: " + ligIds);
    ligCount = ChemCompLiteMod.ligIdsSlctdForInstcVw.length;
	if( ligCount > 0 ){
		$('#help_instnc_brwser_vw').show();
		document.title = CC_LITE_SESSION_DATA.depId+' : Instance Browser View'; 
		loadInstanceBrowserView();
	}
	else{
		alert("Please select at least one entry to submit to Instance Browser View.");
	}
});
/*
$('#help').click(function() {
        alert("[PLACEHOLDER]");
});
*/
window.onbeforeunload = function(evt) {
	//if(checkval==1){
	if(false){
		return 'Your work is not saved! Are you sure you want to close this screen?';
	}
};
//$('#selectall').live("click", function() {
$(document).on("click","#selectall",function() {
	//alert(this.checked);
	$(this).parents('div:eq(0)').find('.selectinstnc').prop('checked', this.checked);
	
	var checked = this.checked;
	if( !checked ){
		ChemCompLiteMod.ligIdsSlctdForInstcVw.length = 0;    	
	}
});
//$('.selectinstnc').live("click", function(){
$(document).on("click",".selectinstnc",function() {
	//alert('Captured click event');
	var thisLigID = $(this).attr('name');
	
	var checked = this.checked;
	if( !checked ){
		$('#selectall').prop('checked', this.checked);
		//$('#'+thisLigID+'_rsrch').prop('checked', this.checked);
		var indx = ChemCompLiteMod.ligIdsSlctdForInstcVw.indexOf(thisLigID)
    	if( indx >= 0 ){
    		ChemCompLiteMod.ligIdsSlctdForInstcVw.splice(indx,1);
        }
	}
});
$(document).on("click","#selectall_rsrch",function() {
	
	var checked = this.checked;
	var ligIdLst = '';
	var separator = '';
	
	if( checked ){
		$(this).parents('div:eq(0)').find('.selectinstnc_rsrch').prop('checked', this.checked);
		//$(this).parents('div:eq(0)').find('.selectinstnc').prop('checked', this.checked);
		//$('#HOH_capture_rsrch_data').show('slow');
		
		$('#ligand_summary_vw :checkbox:checked:not(#selectall):not(.selectinstnc):not(#selectall_rsrch)').each(function( index ) {
	    	thisLigIdRsrch = $(this).attr('name').split("_")[0];
	    	separator = (index > 0) ? "," : "";
	    	ligIdLst += separator + thisLigIdRsrch;
	    });
		
		updateResearchList(ligIdLst,"add");
		
	}else{
		$(this).parents('div:eq(0)').find('.selectinstnc_rsrch:enabled').prop('checked', this.checked);	
		/*if( ! $("#HOH_rsrch").is(':disabled') ){
			$('#HOH_capture_rsrch_data').hide('slow');
		}*/
		
		$('#ligand_summary_vw :checkbox:not(:checked):not(#selectall):not(.selectinstnc):not(#selectall_rsrch)').each(function( index ) {
	    	thisLigIdRsrch = $(this).attr('name').split("_")[0];
	    	separator = (index > 0) ? "," : "";
	    	ligIdLst += separator + thisLigIdRsrch;
	    });
		
		updateResearchList(ligIdLst,"remove");
	}

        // Update background of selection boxess
        updateSummarySelect();
});

function updateResearchList(ligIds,mode){
	$('#hlprfrm_auth_assgnd_grp').val(ligIds);
	$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.UPDATE_RSRCHLST, clearForm: false,
        beforeSubmit: function (formData, jqForm, options) {
            formData.push({"name": "mode", "value": mode});
        }, success: function() {
			$('#hlprfrm_auth_assgnd_grp').val("");
        }
    });
}

$(document).on("click",".selectinstnc_rsrch",function() {
	//alert('Captured click event');
	var thisLigID = $(this).attr('name').split("_")[0];
	var checked = this.checked;
	if( !checked ){
		// if deselected then have to deselect "ALL" for focus of research
		$('#selectall_rsrch').attr('checked', this.checked);
		updateResearchList(thisLigID,"remove");
	}else{
		//$('input.selectinstnc[name="'+thisLigID+'"]').prop('checked', this.checked);
		updateResearchList(thisLigID,"add");
	}

        // Update background of selection boxess
        updateSummarySelect();
});

/*$(document).on("click", 'input.selectinstnc_rsrch[name="HOH"]', function(){
	var checked = this.checked;
	if( checked ){
		$('#HOH_capture_rsrch_data').show('slow');
		//$('.add-h2o-rsrch-fieldset').hide();
	}else{
		$('#HOH_capture_rsrch_data').hide('slow');
	}
});
*/

$(document).on("click", ".addanother_rsrch", function(event){
	var splitArray = $(this).attr('id').split("_");
	var indx = splitArray[3];
	var ligId = splitArray[2];
	//alert("indx: "+indx+" and ligID: "+ligId);
	var srcSelector = "#rsrch_data_set_"+ligId+"_"+(parseInt(indx))+"_";
	var clonedSrc = $(srcSelector).clone().html();
	var updatedSrc = clonedSrc.replaceAll( '_'+parseInt(indx)+'_', '_'+(parseInt(indx)+1)+'_' );
	if( ligId == "HOH"){
		updatedSrc = updatedSrc.replaceAll('Site - '+(parseInt(indx)+1), 'Site - '+(parseInt(indx)+2) );
	}else{
		updatedSrc = updatedSrc.replaceAll('Assay Data - '+(parseInt(indx)+1), 'Assay Data - '+(parseInt(indx)+2) );
	}	
	updatedSrc = updatedSrc.replaceAll('displaynone', '');
	
	var newRsrchSetId = 'rsrch_data_set_'+ligId+'_'+(parseInt(indx)+1)+"_";
	$(srcSelector).after( '<div id="'+newRsrchSetId+'" class="rsrch_data_set" >' );
	
	// display content for new dataset to be captured
	$('#'+newRsrchSetId).append(updatedSrc);
	
	$('#'+newRsrchSetId+' input:not([type="button"])').val('');
	$('#'+newRsrchSetId+' select').val('');
	$('#'+newRsrchSetId+' textarea').val('');
	$('#'+newRsrchSetId+' .disabled_2').attr('disabled','disabled');
	$('#'+newRsrchSetId+' .disabled_3').attr('disabled','disabled');
	$('#'+newRsrchSetId+' .disabled_4').attr('disabled','disabled');
	
	// 	hide dataset action buttons for current set
	$( '#binding_dataset_actions_'+ligId+'_'+(parseInt(indx))+"_" ).hide();
	
	if( parseInt(indx) == 3 ){ 
		$( '#addanother_rsrch_'+ligId+'_'+(parseInt(indx)+1)+"_").hide();
		//i.e. we want to limit user to 5 total binding sets
	}
	
	applyBeautyTips();
	//$("#rsrch_data_set_"+ligId+"_"+(parseInt(indx)+1)).show('slow');
});

$(document).on("click", ".deletethis_rsrch", function(event){
	var splitArray = $(this).attr('id').split("_");
	var indx = splitArray[3];
	var ligId = splitArray[2];
	var srcSelector = "#rsrch_data_set_"+ligId+"_"+(parseInt(indx))+"_";
	
	$(srcSelector).remove();
	
	$( '#binding_dataset_actions_'+ligId+'_'+(parseInt(indx)-1)+"_" ).show();
	if( indx > 1 ){
		$( '#deletethis_rsrch_'+ligId+'_'+(parseInt(indx)-1)+"_" ).show();
	}

});

$(document).on("click", ".copy_rsrch_dscrptr_str", function(event){
	var splitArray = $(this).attr('id').split("_");
	var indx = splitArray[6];
	var ligId = splitArray[5];
	
	var bCanProceed = true;
	
	var srcDcrsptrType = $("#dscrptr_type_"+ligId).val();
	var srcDcrsptrStr = ($("#dscrptr_str_"+ligId).val()).trim();
	
	if( srcDcrsptrStr.length == 0 ){
		alert("Descriptor string not provided in Ligand Verification section.");
		bCanProceed = false;
	}
	
	if( bCanProceed ){
		var trgtDscrptrType = "#rsrch_dscrptr_type_"+ligId+"_"+(parseInt(indx))+"_";
		var trgtDscrptrStr = "#rsrch_dscrptr_str_"+ligId+"_"+(parseInt(indx))+"_";
		$(trgtDscrptrType).val(srcDcrsptrType);
		$(trgtDscrptrStr).val(srcDcrsptrStr);
		$(trgtDscrptrStr).removeAttr('disabled');
	}
	

});

$(document).on("change", '.capture_rsrch_data_input.assay_type', function(event) {
	
	var inputVal = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[(splitArr.length-3)];
	var index = splitArr[(splitArr.length-2)];
	var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
	
	if( inputVal && inputVal.length > 0 ){
		$("#rsrch_data_set_"+authAssgnGrp+"_"+index+"_ .disabled_2").removeAttr('disabled');
		//$("#"+elemId+" option:eq(0)").attr('disabled','disabled');
	}else{
		/**
		$('#rsrch_data_set_'+authAssgnGrp+'_'+index+'_ .capture_rsrch_data_input:not([type="button"])').val("");
		$('#rsrch_data_set_'+authAssgnGrp+'_'+index+'_ .capture_rsrch_data_input:not(.assay_type)').attr('disabled','disabled');
		**/
	}
	
});

$(document).on("change", '.capture_rsrch_data_input.dscrptr_type', function(event) {
	
	var inputVal = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[(splitArr.length-3)];
	var index = splitArr[(splitArr.length-2)];
	var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
	
	if( inputVal && inputVal.length > 1 ){
		$("#rsrch_dscrptr_str_"+authAssgnGrp+"_"+index+"_").removeAttr('disabled');
		
		$("#"+elemId+" option:eq(0)").attr('disabled','disabled');
		
		var dscrptrStrVal = ($("#rsrch_dscrptr_str_"+authAssgnGrp+"_"+index+"_").val()).trim();
		if( dscrptrStrVal && dscrptrStrVal.length > 0 ){
			var bHaveValidVal = checkForValidInput(dscrptrStrVal,inputVal,"notify");
		}
	}else{
		/**
		$("#rsrch_dscrptr_str_"+authAssgnGrp+"_"+index+"_").val("");
		$("#rsrch_dscrptr_str_"+authAssgnGrp+"_"+index+"_").attr('disabled','disabled');
		**/
	}
	
});

$(document).on("change", '.capture_rsrch_data_input.measurement_type', function(event) {
	
	var inputVal = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[(splitArr.length-3)];
	var index = splitArr[(splitArr.length-2)];
	var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
	
	if( inputVal && inputVal.length > 1 ){
		$("#measured_value_"+authAssgnGrp+"_"+index+"_").removeAttr('disabled');
		$("#"+elemId+" option:eq(0)").attr('disabled','disabled');
		var measuredVal = ($("#measured_value_"+authAssgnGrp+"_"+index+"_").val()).trim();
		if( measuredVal && measuredVal.length > 0 ){
			var bHaveValidVal = checkForValidInput(measuredVal,"measured_value","notify");
		}
	}else{
		/**
		$("#measured_value_"+authAssgnGrp+"_"+index+"_").val("");
		$("#measured_value_"+authAssgnGrp+"_"+index+"_").attr('disabled','disabled');
		**/
	}
	
});

$(document).on("keyup", '.capture_rsrch_data_input.measured_value', function(event) {
	
	var inputVal = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[(splitArr.length-3)];
	var index = splitArr[(splitArr.length-2)];
	var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
	
	if( inputVal && inputVal.length > 0 ){
		$("#rsrch_data_set_"+authAssgnGrp+"_"+index+"_ .disabled_3").removeAttr('disabled');
		disableCopyRsrchDscrptr();
	}else{
		/**
		$("#measured_value_"+authAssgnGrp+"_"+index+"_").val("");
		$("#measured_value_"+authAssgnGrp+"_"+index+"_").attr('disabled','disabled');
		**/
	}
	
});

$(document).on("blur", '.capture_rsrch_data_input:not(.rsrch_dscrptr_str):not([type="button"])', function(event) {
	
	var inputVal = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[(splitArr.length-3)];
	var index = splitArr[(splitArr.length-2)];
	var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
	
	
	if( inputVal && inputVal.length > 0 ){
		
		var bHaveValidVal = checkForValidInput(inputVal,inputType,"notify");
		
		if( bHaveValidVal ){
			enableRsrchDataSaveBtn(authAssgnGrp);
		}
	}else{
		if( inputType == "measured_value" ){
			$("#measurement_type_"+authAssgnGrp+"_"+index+"_ option:eq(0)").removeAttr('disabled');
		}
	}	
	
	
});

$(document).on("blur", ".capture_rsrch_data_input.rsrch_dscrptr_str", function(event){

	var dscrptrStr = ($(this).val()).trim();
	var elemId = $(this).attr("id");
	var splitArr = elemId.split("_");
	var authAssgnGrp = splitArr[3];
	var index = splitArr[4];
	var dscrptrType = $("#rsrch_dscrptr_type_"+authAssgnGrp+"_"+index+"_").val();
	
	if( dscrptrStr && dscrptrStr.length > 0 ){
		
		var bHaveValidVal = checkForValidInput(dscrptrStr,dscrptrType,"notify");
		
		if( bHaveValidVal ){
			enableRsrchDataSaveBtn(authAssgnGrp);
		}
	}else{
		$("#rsrch_dscrptr_type_"+authAssgnGrp+"_"+index+"_ option:eq(0)").removeAttr('disabled');
	}
	
	
});


$(document).on("click",".save_rsrch_data", function(){
	//alert("Clicked");
	var request = $(this).attr('value');
	var thisBtn = $(this);
	var authAssgnGrp = $(this).attr('name');
	var dataSubmittedSpanLctr = 'span.datasubmitted_status.'+authAssgnGrp;
	var noDataSubmittedSpanLctr = 'span.no_datasubmitted_status.'+authAssgnGrp;
	var captureRsrchDataFrm = '#capture_rsrch_data_frm_'+authAssgnGrp;
	
	var doSvRsrchData = function(){
		//alert('size of assgnBtns set is: '+$(assgnBtnsLctr).size());
		$('#rsrch_mode_'+authAssgnGrp).val('done');
		if( authAssgnGrp != "HOH" ){
			$('#'+authAssgnGrp+'_capture_rsrch_data .save_rsrch_data').val('Edit Ligand Binding Data');
			$(dataSubmittedSpanLctr).show();
			$(noDataSubmittedSpanLctr).hide();
		}else{
			$('#'+authAssgnGrp+'_capture_rsrch_data .save_rsrch_data').val('Edit');
		}
		
		
		
		$(captureRsrchDataFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_RSRCH_DATA, async: true, clearForm: false,
	        success: function() {
	        	//alert('SUCCESS VERIFICATION MESSAGE HERE');
	        	disableRsrchDataCntrls(authAssgnGrp,'done');
	        	applyRsrchAcqdStatusHighlight(authAssgnGrp);
	        	
	        	// add list of those with data submitted
	        	ChemCompLiteMod.ligIdsWithRsrchSubmitted.push(authAssgnGrp);
	        	
	        	// remove from list of those with data submitted
	        	var indx = ChemCompLiteMod.ligIdsMissingRsrch.indexOf(authAssgnGrp);
	        	if( indx >= 0 ){
	            	ChemCompLiteMod.ligIdsMissingRsrch.splice(indx,1);
	            }
	        	
	        	protectRsrchDataHandler();
	        	
	        }
	    });

	};
	var doUndoRsrchData = function(){
		$('#rsrch_mode_'+authAssgnGrp).val('undo');
		$(dataSubmittedSpanLctr).hide();
		$(noDataSubmittedSpanLctr).show();
		
		if( authAssgnGrp != "HOH" ){
			$('#'+authAssgnGrp+'_capture_rsrch_data .save_rsrch_data').val('Save Ligand Binding Data');
		}else{
			$('#'+authAssgnGrp+'_capture_rsrch_data .save_rsrch_data').val('Save');
		}
		
		$(captureRsrchDataFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_RSRCH_DATA, async: true, clearForm: false,
	       success: function() {
	    	   //alert('SUCCESS VERIFICATION MESSAGE HERE');
	    	   enableRsrchDataCntrls(authAssgnGrp,'undo');
	    	   applyRsrchAcqdStatusHighlight(authAssgnGrp);
	    	   highlightColorRsrchDataSaveBtn(authAssgnGrp);
	    	   
	    	   // add to list of those missing data 
	    	   ChemCompLiteMod.ligIdsMissingRsrch.push(authAssgnGrp);
	    	   
	    	   // remove from list of those with data submitted
	    	   var indx = ChemCompLiteMod.ligIdsWithRsrchSubmitted.indexOf(authAssgnGrp);
	    	   if( indx >= 0 ){
	            	ChemCompLiteMod.ligIdsWithRsrchSubmitted.splice(indx,1);
	           }
	    	   
	    	   protectRsrchDataHandler();
	    	   
	    	   
	        }
	    });
	};
	
	
	if( request.indexOf('Save') >= 0 ){
		var bMissingReqdField = true;
		var validDatasetSubmitted = true;
		var selectorFilter = ( authAssgnGrp != "HOH" ) ? ':not([type="button"])' : '[type="text"]' ;
		var oValidDataSetTracking = new Object();
		
		// First check for at least one non-empty input at all
		$('.c_'+authAssgnGrp+'.capture_rsrch_data_input'+selectorFilter).each( function(indx) {
			var submission = $(this).val();
			var elemId = $(this).attr("id");
			var splitArr = elemId.split("_");
			var index = splitArr[(splitArr.length-2)];
			//console.log("elemId is: "+elemId+" and index is: "+index);
			var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
			
			if( !oValidDataSetTracking.hasOwnProperty(index) ){
				oValidDataSetTracking[index] = new Object();
				oValidDataSetTracking[index].notEmpty = false;
				oValidDataSetTracking[index].validData = true;
				if( authAssgnGrp != "HOH" ){
					oValidDataSetTracking[index].countOfEmptyMeasurementGrpItems = 0;
					oValidDataSetTracking[index].dscrptrMissing = false;
					oValidDataSetTracking[index].dscrptrTypeMissing = false;
					oValidDataSetTracking[index].haveAssayType = true;
				}
			}
			
			if( submission && (submission.trim()).length >= 1 && submission !== authAssgnGrp ){
				oValidDataSetTracking[index].notEmpty = true;				
			}else{
				if( inputType == "assay_type"){
					oValidDataSetTracking[index].haveAssayType = false;
				}				
			}	
		});
		
		// check for collective presence/absence of measurement related data (NOT APPLICABLE FOR WATER) 
		if( authAssgnGrp != "HOH" ){
			
			$('.c_'+authAssgnGrp+'.capture_rsrch_data_input.measurement_grp').each( function(indx) {
				var submission = $(this).val();
				var elemId = $(this).attr("id");
				var splitArr = elemId.split("_");
				var index = splitArr[(splitArr.length-2)];
				
				if( !(submission && submission.length >= 1 ) ){
					oValidDataSetTracking[index].countOfEmptyMeasurementGrpItems += 1;				
				}
			});
			
		}
		
		// Then check validity for text inputs
		$('.c_'+authAssgnGrp+'.capture_rsrch_data_input:not(.rsrch_dscrptr_str):not([type="button"]):not(select)').each( function(indx) {
			
			var inputVal = $(this).val();
			var elemId = $(this).attr("id");
			var splitArr = elemId.split("_");
			var authAssgnGrp = splitArr[(splitArr.length-3)];
			var index = splitArr[(splitArr.length-2)];
			var inputType = elemId.split("_"+authAssgnGrp+"_"+index+"_")[0];
			
			if( inputVal && (inputVal.trim()).length > 0 ){
				var bHaveValidVal = checkForValidInput(inputVal,inputType,"onglobalsave");
				if( !bHaveValidVal ){
					oValidDataSetTracking[index].validData = false;
				}
			}
			
		});
		
		// Special handling for validation check on descriptors
		$('.c_'+authAssgnGrp+'.capture_rsrch_data_input.rsrch_dscrptr_str').each( function(indx) {

			var dscrptrStr = ($(this).val()).trim();
			var elemId = $(this).attr("id");
			//alert(elemId);
			var splitArr = elemId.split("_");
			var authAssgnGrp = splitArr[3];
			var index = splitArr[4];
			//alert(index);
			var dscrptrType = $("#rsrch_dscrptr_type_"+authAssgnGrp+"_"+index+"_").val();
			
			if( dscrptrStr && dscrptrStr.length > 0 ){
				
				if( !(dscrptrType) ){
					oValidDataSetTracking[index].dscrptrTypeMissing = true;
				}else{
				
					var bHaveValidVal = checkForValidInput(dscrptrStr,dscrptrType,"onglobalsave");
					
					if( !bHaveValidVal ){
						oValidDataSetTracking[index].validData = false;
					}
				}
			}else{
				if( dscrptrType && dscrptrType.length > 0 ){
					oValidDataSetTracking[index].dscrptrMissing = true;
				}
			}	
			
			
		});
		
		for( index in oValidDataSetTracking ){
			
			if( !oValidDataSetTracking[index].notEmpty ){ 
				validDatasetSubmitted = false;
				alert("Cannot submit an empty dataset. Please check content in dataset #"+(parseInt(index)+1));
			}else{
				if( authAssgnGrp != "HOH" && !(oValidDataSetTracking[index].haveAssayType) ){
					validDatasetSubmitted = false;
					alert("Cannot submit dataset without specifying the assay type. Please check content in dataset #"+(parseInt(index)+1));
				}
			}
			if( validDatasetSubmitted ){ // if have non-empty set then prompt whether there is still a validity problem
				
				if( !oValidDataSetTracking[index].validData ){ 
					validDatasetSubmitted = false;
					alert("Still have input that requires correction. Please check dataset #"+(parseInt(index)+1));
				}
			}
			if( validDatasetSubmitted ){
				if( authAssgnGrp != "HOH" ){
					if( oValidDataSetTracking[index].countOfEmptyMeasurementGrpItems > 0 ){ 
						validDatasetSubmitted = false;
						alert("Measurement type and measured value must both be provided. Please check dataset #"+(parseInt(index)+1));
					}
					if( oValidDataSetTracking[index].dscrptrMissing ){
						validDatasetSubmitted = false;
						alert("Descriptor type is specified but corresponding string is missing. Please check dataset #"+(parseInt(index)+1));
					}
					if( oValidDataSetTracking[index].dscrptrTypeMissing ){
						validDatasetSubmitted = false;
						alert("Descriptor string is provided but corresponding descriptor type is missing. Please check dataset #"+(parseInt(index)+1));
					}
				}
			}
		}
		
		
		bMissingReqdField = false; // setting to false, need to verify if any fields mandatory
		
		if( bMissingReqdField ){ // if still have no data after all of checks above then prompt user
			alert('One of the required fields is missing.');
		}
		else if( validDatasetSubmitted ){
			doSvRsrchData();
		}
	}
	else{
		doUndoRsrchData();
	}
	
});

////////////////////END OF EVENT HANDLERS - Global Ligand Summary View //////////////////////////////////////////////////////
