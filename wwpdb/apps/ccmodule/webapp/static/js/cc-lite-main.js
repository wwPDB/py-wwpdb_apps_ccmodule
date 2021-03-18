/***********************************************************************************************************
File:		cc-lite-main.js
Author:		rsala (rsala@rcsb.rutgers.edu)
Date:		2010-10-01
Version:	0.0.1

JavaScript supporting Ligand Lite Module web interface 

2010-10-01, RPS: Created
2013-02-22, RPS: Updates per change in UI design to adopt strategy of "exact match" searching intead of "ID match" searching
2013-04-02, RPS: Added support for tracking of ligand groups for which mismatches are addressed by depositor.
2013-07-03, RPS: Added validation checking of any values submitted for "alternate ligand ID".
2013-07-23, RPS: URLs added for user requested handling of uploaded files.
2013-12-13, RPS: Updates as part of fix for failed processing in Chrome and Internet Explorer.
2014-01-21, RPS: Updated references to imported javascript for jqueryUI, Jsmol, BeautyTips plugin
2014-01-22, RPS: Reverting back to referencing unminified versions of cc-lite-global and cc-lite-instance view js files
					due to unexpected problems arising from use of minified versions
2014-01-22, RPS: Reinstating use of minified versions of custom javascript files.
					Updated to provide navigation buttons at bottom of screen in instance level view		
2014-03-19, RPS: Instituted workaround to allow handling of URL references with custom prefixes.
2016-04-28, RPS: Parameterizing for choice of JMOL_VRSN and currently setting to "jmol-latest" 
2016-04-13, RPS: Updated to remove all AJAX calls where async option was set to 'false'. 
2016-06-27, RPS: Synchronizing list of accepted file types for uploaded chemical image files
2017-01-30, RPS: Updates to support capturing info for ligands as "focus of research"
2017-02-07, RPS: Improved handling of validation for data input for ligands as "focus of research".
2017-02-10, RPS: Updated regex used for smiles validation to allow for shorter descriptor lengths (e.g. O=C=O)
2017-02-14, RPS: Updates for UI controls behavior.
2017-02-15, RPS: Removing "Save (and come back later) button which has become obsolete.
2017-02-16-17, RPS: Updates to accommodate additional validation requirements.
*************************************************************************************************************/
var ChemCompLiteMod = {
	ajaxTimeout: 60000,
	SNGL_INSTNC: "ChemCompLiteMod.SNGL_INSTNC",
	ALL_INSTNC: "ChemCompLiteMod.ALL_INSTNC",
	adminContact: 'Send comments to: <a href="mailto:jwest@rcsb.rutgers.edu">help@wwpdb-dev.rutgers.edu</a>',
	infoStyle: '<span class="ui-icon ui-icon-info fltlft"></span> ',
	errStyle: '<span class="ui-icon ui-icon-alert fltlft"></span> ',
	activeCCid: 1,
	debug: false,
	loadSmmryFrmLctr: '#load_smmry_frm',
	ligIdsSlctdForInstcVw: new Array(),
	ligIdsCrrntlyInInstcVw: new Array(),
	ligIdsRslvd: new Array(),
	ligIdsWithRsrchSubmitted: new Array(),
	ligIdsMissingRsrch: new Array(),
	ligIdsMismatched: new Array(),
	currBrowser: "",
	dataAvail: "no",
	URL: {
		GEN_LIG_SMMRY_RSLTS: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/view/ligandsummary',
		GET_LIGAND_SUMMARY: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/report/summary',
		GET_REPORT_FILE: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/report/file',
		GET_REPORT_STATUS: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/report/status',
		CHECK_FOR_SMMRY_DATA: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/view/ligandsummary/data_check',
		LOAD_LIG_SMMRY_DATA: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/view/ligandsummary/data_load',
		LOAD_INSTNC_BRWSR: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/view/instancebrowser',
		SAVE_NW_LGND_DSCR: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/save/newligdescr',
		SAVE_EXCT_MTCH_ID: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/save/exactmtchid',
		SAVE_RSRCH_DATA: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/save/rsrchdata',
		UPDATE_RSRCHLST: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/updatersrchlst',
		EXIT_FINISHED: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/wf/exit_finished',
		EXIT_NOT_FINISHED: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/wf/exit_not_finished',
		VALIDATE_CCID: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/validate_ccid',
		CHECK_FOR_UPLOADED_FILES: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/check_uploaded_files',
		REMOVE_UPLOADED_FILE: CC_LITE_SESSION_DATA.servicePathPrefix+'/service/cc_lite/remove_uploaded_file'
	},
	accptdImgFileTypes: CC_LITE_SESSION_DATA.accptdImgFileTypes,
	accptdDefFileTypes: CC_LITE_SESSION_DATA.accptdDefFileTypes,
	JMOL_VRSN: 'jmol-latest',
	inputTypeValidation: new Object()
};

$(document).ready(function() {	
	$('.errmsg.glblerr').ajaxError(function(e, x, settings, exception) {
	    try {
	        if (x.status == 0) {
	            $(this).html(ChemCompLiteMod.errStyle + 'You are offline!!<br />Please Check Your Network.').show().fadeOut(4000);
	        } else if (x.status == 404) {
	            $(this).html(ChemCompLiteMod.errStyle + 'Requested URL "' + settings.url + '" not found.<br />').show().fadeOut(4000);
	        } else if (x.status == 500) {
	            $(this).html(ChemCompLiteMod.errStyle + 'Internel Server Error.<br />').show().fadeOut(4000);
	        } else if (e == 'parsererror') {
	            $(this).html(ChemCompLiteMod.errStyle + 'Error.\nParsing JSON Request failed.<br />').show().fadeOut(4000);
	        } else if (e == 'timeout') {
	            $(this).html(ChemCompLiteMod.errStyle + 'Request Time out.<br />').show().fadeOut(4000);
	        } else {
	            $(this).html(ChemCompLiteMod.errStyle + x.status + ' : ' + exception + '<br />\n').show().fadeOut(4000);
	        }
	    } catch (err) {
			$('.loading').hide();
	        var errtxt = 'There was an error while processing your request.\n';
	        errtxt += 'Error description: ' + err.description + '\n';
	        errtxt += 'Click OK to continue.\n';
	        alert(errtxt);
	    }
	});
	
	// set up regex validation for data inputs
	ChemCompLiteMod.inputTypeValidation.displaytext = new Object();
	ChemCompLiteMod.inputTypeValidation.target_sequence = /\w/;
	ChemCompLiteMod.inputTypeValidation.displaytext.target_sequence = "target sequence value";
	ChemCompLiteMod.inputTypeValidation.ph = /^(?:14(?:\.0)?|1[0-3](?:\.[0-9])?|[1-9](?:\.[0-9])?|0?\.[0-9])$/;
	ChemCompLiteMod.inputTypeValidation.displaytext.ph = "pH value";
	ChemCompLiteMod.inputTypeValidation.assay_temp = /^([0-9](?:\.[0-9])?|[1-9][0-9](?:\.[0-9])?|1[0-9][0-9](?:\.[0-9])?|2[0-9][0-9](?:\.[0-9])?|3[0-9][0-9](?:\.[0-9])?|400)$/;
	ChemCompLiteMod.inputTypeValidation.displaytext.assay_temp = "temperature value";
	ChemCompLiteMod.inputTypeValidation.measurement_type = /\w/;
	ChemCompLiteMod.inputTypeValidation.displaytext.measurement_type = "measurement type";
	ChemCompLiteMod.inputTypeValidation.measured_value = /^\s*-?(([0-9]+)[.]?|([0-9]*[.][0-9]+))([(][0-9]+[)])?([eE][+-]?[0-9]+)?\s*$/;
	ChemCompLiteMod.inputTypeValidation.displaytext.measured_value = "measured value";
	ChemCompLiteMod.inputTypeValidation.residuenum = /\d/;
	ChemCompLiteMod.inputTypeValidation.displaytext.residuenum = "residue number";
	ChemCompLiteMod.inputTypeValidation.chain_id = /\w/;
	ChemCompLiteMod.inputTypeValidation.displaytext.chain_id = "chain ID";
	ChemCompLiteMod.inputTypeValidation.smiles = /^([^J][0-9BCOHNSOPrIFlagWZn@+\-\[\]\(\)\\\/\|%=#$]{2,})$/i;
	ChemCompLiteMod.inputTypeValidation.displaytext.smiles = "SMILES string";
	ChemCompLiteMod.inputTypeValidation.inchi = /^((InChI=)?[^J][0-9BCOHNSOPrIFlagZn+\-\(\)\\\/,\.;\*pqbtmsih]{6,})$/i;
	ChemCompLiteMod.inputTypeValidation.displaytext.inchi = "InChi string";
		
	//window.postMessage("hello parent",'http://wwpdb-deploy-test-2.wwpdb.org/deposition//pageview/ligandsummary'); //send the message and target URI
	
	/** pilot code for exploring iframeChild-to-parentWindow messaging
	$.ajax({url: '/ccmodule_lite/js/jquery/plugins/jquery.ba-postmessage.js', async: false, dataType: 'script'});
	$.postMessage(
		CC_LITE_SESSION_DATA.sessionID,
		'http://wwpdb-deploy-2.wwpdb.org/deposition//pageview/ligandsummary',
		parent
	);
	***/	
	/**$('#help_glbl_smmry_vw').bt({positions: ['left','bottom'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#summary',ajaxOpts:{dataType:'html'},trigger: 'click',
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});**/
	$('div.savedone').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#finish',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.instance_browser_ui').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#instnc_srch_scrn',ajaxOpts:{dataType:'html'},trigger: 'hover',
	width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
	strokeStyle: '#ABABAB',strokeWidth: 1});
	$('.back_to_summary_vw').bt({positions: ['bottom','left','top'],ajaxPath: CC_LITE_SESSION_DATA.servicePathPrefix+'/ccmodule_lite/cc_help.html div#lgnd_summry_scrn',ajaxOpts:{dataType:'html'},trigger: 'hover',
		width: 600,centerPointX: .9,spikeLength: 20,spikeGirth: 10,padding: 15,cornerRadius: 25,fill: '#FFF',
		strokeStyle: '#ABABAB',strokeWidth: 1});
});	

