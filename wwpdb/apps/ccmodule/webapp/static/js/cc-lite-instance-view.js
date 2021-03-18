/****************************************************************************************************************************
File:		cc-lite-instance-view.js
Author:		rsala (rsala@rcsb.rutgers.edu)

JavaScript supporting Ligand Lite Module web interface 

2011-12-08, RPS: This file created to house code for managing "instance level view" and which originally came from ligmod.js
2012-12-18, RPS: Updated to provide proper disabling of controls on commit of new ligand description for a ligand group.
2013-02-22, RPS: Updates per change in UI design to adopt strategy of "exact match" searching intead of "ID match" searching
2013-03-18, RPS: Addressed bug whereby "Commit" button was not enabled on use of the MarvinSketch editor.
2013-03-19, RPS: Improved processing re: sketch vs. descriptor string inputs
2013-04-02, RPS: Improved visual cues signaling when mismatches are addressed by depositor.
2013-07-03, RPS: Added validation checking of any values submitted for "alternate ligand ID".
2013-07-23, RPS: Updates for user-requested handling of uploaded files.
2013-09-30, RPS: Improving user experience on "Commit" of new ligand description.
2013-10-15, RPS: Further improvements of screen behavior on "Commit" of new ligand description.
2013-10-18, RPS: Added option to clear incorrectly specified paths for file uploads.
2014-01-21, RPS: Updated event binding calls per update in jquery core to 1.10.2
					Replaced use of applet Jmol with javascript Jsmol.
					Removed provision for chem diagram editor until issues with MarvinSketch can be resolved.
					Upload of image file now in "required" section.
					Checking for previously uploaded files now distinguishing between image files and component definition files.
2014-01-23, RPS: Displaying confirmation of component-image files previously uploaded.
2014-01-31, RPS: Fix for problematic Save/Undo label toggling for .save_descr class buttons.
2014-02-03, RPS: Updated with check for and display of confirmation for already uploaded component-definition files.
					Also added validation of SMILES/InChi strings.
2014-03-11, RPS: Fix to ensure JSmol launch for different ligand instances but which share proposed ligand ID and residue number components.
					Taking safe approach of destroying JSmol instance and creating each time instance view is revisited.
2014-03-20, RPS: Styling for missing required info made more consistent to that of rest of Dep UI.					
2014-03-26, RPS: "mode" of do/undo SvNwLgndDscr and do/undo SvExactMtchId being handled as formal form inputs to safeguard against loss
 					of parameter being seen in rare (reupload?) cases.
 					Same strategy to replace use of all dynamically formData.push parameters.
2014-05-02, RPS: Added more help dialogs to clarify that only single file is used for a given ligand ID when handling uploads for either 
					image files or component definition files.
2014-06-06, RPS: Improved display of dialogs confirming files already uploaded, so that these are always visible relative to the button pressed.					
2014-06-17, RPS: Corrected toggling of "attn_reqd" display highlighting in sitations where some instances pass while other instances mismatch.
2014-06-23, RPS: Updates in support of providing more elaborate choices for choosing an alternate Ligand ID
 				 (originally proposed ID vs. one of the possible exact match IDs for cases where some ligand instances have 
 				 differing matches).
2016-04-28, RPS: Parameterizing for choice of JMOL_VRSN and currently setting to "jmol-latest"  				 
2016-04-13, RPS: Updated to remove all AJAX calls where async option was set to 'false'. 
2016-06-27, RPS: Synchronizing list of accepted file types for uploaded chemical image files
2017-02-03, RPS: Updated to support capture of data for ligands as "focus of research"
2017-02-07, RPS: Improved handling of validation for data input for ligands as "focus of research".
2017-02-08, RPS: Updates for button labels and tooltip behavior.
2017-02-14, RPS: Updates for input validation checking.
2017-02-17, RPS: Updating "Undo" to "Edit" for labels of controls for capturing data.
*****************************************************************************************************************************/
////////////////////START: FUNCTION DEFINITIONS - Instance Browser View //////////////////////////////////////////////////////

var jsmolAppOpen={};
var jsmolAppDict={};

function initJsmolApp(appName, id) {
	//alert("Beginning initJsmolApp");
    var xSize=300;
    var ySize=300;
    Jmol._binaryTypes = [".map",".omap",".gz",".jpg",".png",".zip",".jmol",".bin",".smol",".spartan",".mrc",".pse"];
    Info = {
        j2sPath: "/assets/applets/"+ChemCompLiteMod.JMOL_VRSN+"/jsmol/j2s",
        serverURL: "/assets/applets/"+ChemCompLiteMod.JMOL_VRSN+"/jsmol/php/jsmol.php",
	//	serverURL: "http://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
        width:  xSize,
        height: ySize,
        debug: false,
        color: "0xD3D3D3",
        disableJ2SLoadMonitor: true,
        disableInitialConsole: true,
        addSelectionOptions: false,
        use: "HTML5",
        readyFunction: null,
        script: ""
    };
    Jmol.setDocument(0);
    jsmolAppDict[appName]=Jmol.getApplet(appName,Info);


    $('#'+id).html( Jmol.getAppletHtml(jsmolAppDict[appName]) );
    jsmolAppOpen[appName]=true;
    
    //alert("Reached end of initJsmolApp and html is: "+Jmol.getAppletHtml(jsmolAppDict[appName]));
}


function loadFileJsmol(appName, id, filePath, jmolMode) {
	//alert("in loadFileJsmol and filePath is: "+filePath);
	if( jsmolAppOpen[appName] ) {
		delete jsmolAppDict[appName];
		jsmolAppOpen[appName]=false;
    }
	initJsmolApp(appName,id);
	
    var setupCmds = '';
    if (jmolMode == 'wireframe') {
    	setupCmds = "background black; wireframe only; wireframe 0.05; labels off; slab 100; depth 40; slab on;";
    } else if (jmolMode == 'cpk') {
    	setupCmds = "background white; wireframe off; spacefill on; color chain; labels off; slab 100; depth 40; slab on";
    } else {
    	setupCmds = "";
    }
    var jmolCmds = "load " + filePath + "; " + setupCmds;
    Jmol.script(jsmolAppDict[appName], jmolCmds);
}

function toggleChemCompDisplay(sInstId,sRefId,sCntxt,bShow){
	var id_1, id_2, jmolHtmlSuffix, atmMpHtmlSuffix;
	if( sCntxt == ChemCompLiteMod.SNGL_INSTNC ){
		id_1 = sInstId;
		id_2 = sRefId;
		jmolHtmlSuffix = '_ref_jmol.html';
	}
	else if( sCntxt == ChemCompLiteMod.ALL_INSTNC ){
		id_1 = sRefId;
		id_2 = sInstId;
		jmolHtmlSuffix = 'instnc_jmol_allInstVw.html';
	}
	var ulElemLocator = ' #instance_data_' + id_1;
	var liElemUrl = CC_LITE_SESSION_DATA.sessPathPrefix + '/' + sInstId +'/'+id_2+'_viz_cmp_li.html';
	var liElemLocator = ' #vizcmp_' + id_1 + '_' + id_2;
	//alert('Length of '+liElemLocator+' is : '+$(liElemLocator).length );
	if( $(liElemLocator).length == 0){
		$.get(liElemUrl, function(data){
			$(ulElemLocator).append(data);
			var twoDchecked = $('#twoD_chck_bx_'+id_1).prop("checked");
			var threeDchecked = $('#threeD_chck_bx_'+id_1).prop("checked");
			var twoDdivElemLocator = liElemLocator + ' div.twoDviz';
			var threeDdivElemLocator = liElemLocator + ' div.threeDviz';
			var jmolHtmlUrl = CC_LITE_SESSION_DATA.sessPathPrefix + '/' + sInstId +'/'+id_2+jmolHtmlSuffix;
			$(twoDdivElemLocator).css('display', twoDchecked ? 'block' : 'none');
			if( $(threeDdivElemLocator).length < 100 ){
				$(threeDdivElemLocator).load(jmolHtmlUrl, function(){
					$(threeDdivElemLocator).css('display', threeDchecked ? 'block' : 'none');
				});
			}
		}, "html");
	}
	$(liElemLocator).css('display', bShow ? 'block' : 'none');
}

function disableDscrLgndCntrls(ligid,mode) {
	$('.descr_nw_lgnd_input.c_'+ligid).each(function() {
		$(this).attr('disabled','disabled');
	});
	$('.addrss_msmtch.c_'+ligid).each(function() {
		$(this).attr('disabled','disabled');
	});
	/***
	var mrvnSktch = eval('document.MSketch_'+authAssgnGrp);
	if( mrvnSktch != null ) {
		mrvnSktch.setParams('viewonly=true');
	}
	***/
	
	if( mode == 'done'){
		$('#launch_editor_'+ligid).val('Launch Editor');
		$('#chem_diagram_'+ligid).hide("slow");
	}
	else if( mode == 'validate'){
		$('.descr_new_lgnd_submit_'+ligid).attr('disabled','disabled');
	}
}

function enableDscrLgndCntrls(ligid,mode) {
	$('.descr_nw_lgnd_input.c_'+ligid).each(function() {
		$(this).removeAttr('disabled');
	});
	$('.addrss_msmtch.c_'+ligid).each(function() {
		$(this).removeAttr('disabled');
	});
	$('#marvin_'+ligid).show('slow');
	if( mode == 'undo'){
		$('.descr_new_lgnd_submit_'+ligid).val('Save Verification for Ligand Mismatch');
	}
	else if( mode == 'validate'){
		$('.descr_new_lgnd_submit_'+ligid).removeAttr('disabled');
	}
}

function applyRsrchAcqdStatusHighlight(ligId){
	$('#'+ligId+'_rsrch_hdr').toggleClass("data_acqurd");
	$('#'+ligId+'_rsrch_hdr').toggleClass("no_data_acqurd");

}

function applyRslvStatusHighlight(ligId){
	var hdrLctr = '.'+ligId+'_hdr';
	$(hdrLctr).not(".rsrch_data").each( function() {
		$(this).toggleClass("is_rslvd");
	});
	$('ul.jPag-pages li').each( function(index) {
		var ccId = $(this).text();
		if( ccId.toLowerCase() == ligId.toLowerCase() ){
			$(this).toggleClass("is_rslvd");
		}
	});
}

function trackRslvdLigIds(){
	var ligIds = "";
	// DEBUG alert("Length of ChemCompLiteMod.ligIdsRslvd now: "+ChemCompLiteMod.ligIdsRslvd.length);
	for( x=0; x < ChemCompLiteMod.ligIdsRslvd.length; x++ ){
    	thisLigID = ChemCompLiteMod.ligIdsRslvd[x];
    	// DEBUG alert("x="+x+" and thisLigID now: "+thisLigID);
    	ligIds += ((ligIds.length > 0) ? ',' : '') + thisLigID;
    }
    $('#rslvdlist').val(ligIds);
}

function collapseAllAccordions(grpId){
	//so that we eliminate user effort to scroll back up to top of page
	
	$("#"+grpId+"_inneraccordion span.ui-icon").removeClass('ui-icon-circle-arrow-s').addClass('ui-icon-circle-arrow-e');
	$("#"+grpId+"_inneraccordion .single_instance").hide('slow');
	$("#"+grpId+"_inneraccordion .all_instances").hide('slow');
	$('#mainContent').scrollTop(0);
	window.parent.$("div:first").scrollTop(0);
}

function clearFileUpload(fileInputId){
	var styleStr = '';
	var classStr = '';
	//<input type='file' size='50' id="file_img_%(auth_assgnd_grp)s" name="file_img"  style="margin-left: 15px;" class="c_%(auth_assgnd_grp)s file_upload descr_nw_lgnd_input fltlft reqd" %(disabled)s/>
	//<input type='file' size='50' id="file_refdict_%(auth_assgnd_grp)s" name="file_refdict" class="c_%(auth_assgnd_grp)s file_upload descr_nw_lgnd_input file_refdict fltlft" %(disabled)s />
	var grpId = fileInputId.split('_')[2];
	//alert("grpId: "+grpId);
	var inputName = fileInputId.split("_"+grpId)[0];
	//alert("inputName: "+inputName);
	if( inputName == "file_img"){
		styleStr = 'style="margin-left: 15px;"';
		classStr = "reqd";
	}
	else{
		classStr = "file_refdict";
	}
	$("#"+fileInputId).replaceWith('<input type="file" size="50" id="'+fileInputId+'" name="'+inputName+'" '+styleStr+' class="c_'+grpId+' file_upload descr_nw_lgnd_input fltlft '+classStr+'"/>');
	
	checkMissingAssrtdReqdFields(grpId);
	checkCompDefFileUploads(grpId,"refresh");
}

function getUniqueIdForJsmol(sInstId){
	return sInstId.split("_")[1]+sInstId.split("_")[2]+sInstId.split("_")[3];
}

//////////////////// END: FUNCTION DEFINITIONS - Instance Browser View //////////////////////////////////////////////////////	

//////////////////// BEGIN: EVENT HANDLERS - Instance Browser View //////////////////////////////////////////////////////
$(document).on("click",".clearupld", function(){
	var thisBtn = $(this);
	var thisBtnId = $(this).attr('id');
	var targetInputId = thisBtnId.split("clear_")[1];
	//alert('targetInputId: '+targetInputId);
	clearFileUpload(targetInputId);
});

$(document).on("click",".save_descr", function(){
	//alert("Clicked");
	var request = $(this).attr('value');
	var thisBtn = $(this);
	var authAssgnGrp = $(this).attr('name');
	var hdrLctr = '.'+authAssgnGrp+'_hdr';
	var spanLctr = '.resolve_status.'+authAssgnGrp;
	var batchRsltsTbl = '#allinst_match_tbl_'+authAssgnGrp;
	var descrNwLgndFrm = '#descr_nw_lgnd_frm_'+authAssgnGrp;
	var typeOfLgndVlu = $(descrNwLgndFrm+' input:radio[name=lgnd_type_'+authAssgnGrp+']:checked').val();
	var doneBtnLctr = '.descr_new_lgnd_submit_'+authAssgnGrp;
	var rslvStatusSpanLctr = 'span.resolve_status.'+authAssgnGrp;
	var attnReqdSpanLctr = 'a.'+authAssgnGrp+'_hdr.attn_reqd span.attn_reqd.'+authAssgnGrp;
	var glblBatchRsltsTbl = '#ligand_inventory_tbl';
	var instAssgnChngCnt = 0;
	var instIdList = '';
	var numMsmtchAddrssdInGrp = Number( $('#'+authAssgnGrp+'_msmtch_addrssd_cnt').html() );
	var molDataStr = '';

	var doSvNwLgndDscr = function(){
		$('#all_instncs_'+authAssgnGrp+' .save_descr').val('Edit Verification for Ligand Mismatch');
		//alert('size of assgnBtns set is: '+$(assgnBtnsLctr).size());
		$('#mode_'+authAssgnGrp).val('done');
		$(rslvStatusSpanLctr).show();
		$(attnReqdSpanLctr).hide();
		
		$(glblBatchRsltsTbl+' tr.c_'+authAssgnGrp+' .resolve_status').each( function() {
			$(this).html('Mismatch(es) Addressed');
			$(this).removeClass('warn');
		});
		//numMsmtchAddrssdInGrp = numMsmtchAddrssdInGrp + instAssgnChngCnt;
		//$('#'+authAssgnGrp+'_assgn_cnt').html(numMsmtchAddrssdInGrp);
		
		$(descrNwLgndFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_NW_LGND_DSCR, async: true, clearForm: false,
	        success: function() {
	        	//alert('SUCCESS VERIFICATION MESSAGE HERE');
	        	disableDscrLgndCntrls(authAssgnGrp,'done');
	        	applyRslvStatusHighlight(authAssgnGrp);
	        	ChemCompLiteMod.ligIdsRslvd.push(authAssgnGrp);
	        	trackRslvdLigIds();
	        	checkForUploadedImageFiles(authAssgnGrp,"requirementscheck");
	        	checkCompDefFileUploads(authAssgnGrp,"refresh");
	        	//below so that we eliminate user effort to scroll back up to top of page
	        	//collapseAllAccordions(authAssgnGrp);
	        	
	        }
	    });

	};
	var doUndoNwLgndDscr = function(){
		$('#all_instncs_'+authAssgnGrp+' .save_descr').val('Save Verification for Ligand Mismatch');
		$('#mode_'+authAssgnGrp).val('undo');
		$(rslvStatusSpanLctr).hide();
		$(attnReqdSpanLctr).show();
		
		$(glblBatchRsltsTbl+' tr.c_'+authAssgnGrp+' .resolve_status').each( function() {
			$(this).html('Mismatch(es) Require Attention');
			$(this).addClass('warn');
		});
		
		//numAssgndInGrp = numAssgndInGrp - instAssgnChngCnt;
		//$('#'+authAssgnGrp+'_assgn_cnt').html(numAssgndInGrp);
		
		$(descrNwLgndFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_NW_LGND_DSCR, async: true, clearForm: false,
	       success: function() {
	        	//alert('SUCCESS VERIFICATION MESSAGE HERE');
	        	enableDscrLgndCntrls(authAssgnGrp,'undo');
	        	applyRslvStatusHighlight(authAssgnGrp);
	        	
	        	var indx = ChemCompLiteMod.ligIdsRslvd.indexOf(authAssgnGrp);
	        	if( indx >= 0 ){
	            	ChemCompLiteMod.ligIdsRslvd.splice(indx,1);
	            }
				trackRslvdLigIds();
	        }
	    });
	};
	
	
	if( request.indexOf('Save') >= 0 ){
		var mrvnSktch = eval('document.MSketch_'+authAssgnGrp);
		var bMissingReqdField = true;
		var dscrptrStr = ($('#dscrptr_str_'+authAssgnGrp).val()).trim();
		var dscrptrType = $('#dscrptr_type_'+authAssgnGrp).val();
		var noDscrptrStrProblem = true;
		if( dscrptrStr && dscrptrStr.length > 0 ){
			noDscrptrStrProblem = checkForValidInput(dscrptrStr,dscrptrType,"notify");
		}
		
		bMissingReqdField = ( checkMissingLigandTypeField(authAssgnGrp) || checkMissingAssrtdReqdFields(authAssgnGrp) );

		if( bMissingReqdField ){ // if still have no data after all of checks above then prompt user
			alert('One of the required fields is missing.');
		}
		else{
			if( noDscrptrStrProblem ){
				var invalidCcId = false;
				var altrntCcId = $('#alt_ccid_'+authAssgnGrp).val();
				
				if( altrntCcId.length > 1 ){
					$('#vldtmode_'+authAssgnGrp).val('full');
					$(descrNwLgndFrm).ajaxSubmit({url: ChemCompLiteMod.URL.VALIDATE_CCID, async: true, clearForm: false,
				        success: function(jsonObj) {
				        		if (jsonObj.errorflag) {
				        			alert("There was a problem with the 'Alternate Ligand ID' you provided. "+jsonObj.errortext);
				        			invalidCcId = true;
				        		}else{
				        			doSvNwLgndDscr();
				        		}
				        }
					});
				}else{
					doSvNwLgndDscr();
				}
			}
		}
	}
	else{
		doUndoNwLgndDscr();
	}
	
});

$(document).on("click",".addrss_msmtch_opts .save_exact_mtch_id", function(){
	//alert("Clicked");
	var request = $(this).attr('value');
	var thisBtn = $(this);
	var authAssgnGrp = $(this).attr('name');
	var addrssMsmtchOptsFrm = '#addrss_msmtch_opts_frm_'+authAssgnGrp;
	var hdrLctr = '.'+authAssgnGrp+'_hdr';
	var doneBtnLctr = '#addrss_msmtch_opts_submit_'+authAssgnGrp;
	var glblBatchRsltsTbl = '#ligand_inventory_tbl';
	var radioInputsLctr = '.addrss_msmtch.c_'+authAssgnGrp;
	var rslvStatusSpanLctr = 'span.resolve_status.'+authAssgnGrp;
	var attnReqdSpanLctr = 'a.'+authAssgnGrp+'_hdr.attn_reqd span.attn_reqd.'+authAssgnGrp;
	//var instAssgnChngCnt = 0;
	//var instIdList = '';
	//var numMsmtchAddrssdInGrp = Number( $('#'+authAssgnGrp+'_msmtch_addrssd_cnt').html() );
	
	var doSvExactMtchId = function(){
		$(thisBtn).val('Edit Verification for Ligand Mismatch');
		//alert('size of assgnBtns set is: '+$(assgnBtnsLctr).size());
		$('#exactmatchid_mode_'+authAssgnGrp).val('done');
		
		$(rslvStatusSpanLctr).show();
		$(attnReqdSpanLctr).hide();
		
		$(glblBatchRsltsTbl+' tr.c_'+authAssgnGrp+' .resolve_status').each( function() {
			$(this).html('Mismatch(es) Addressed');
			$(this).removeClass('warn');
		});
		//numMsmtchAddrssdInGrp = numMsmtchAddrssdInGrp + instAssgnChngCnt;
		//$('#'+authAssgnGrp+'_assgn_cnt').html(numMsmtchAddrssdInGrp);
		
		$(radioInputsLctr).each(function() {
			$(this).attr('disabled','disabled');
		});
		
		$(addrssMsmtchOptsFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_EXCT_MTCH_ID, async: true, clearForm: false,
			success: function() {
        		applyRslvStatusHighlight(authAssgnGrp);
        		ChemCompLiteMod.ligIdsRslvd.push(authAssgnGrp);
	        	trackRslvdLigIds();
	        	//alert('COMMIT: SUCCESS VERIFICATION MESSAGE HERE');
	        	
	        	//below so that we eliminate user effort to scroll back up to top of page
	        	//collapseAllAccordions(authAssgnGrp);
	        }
	    });

	};
	var doUndoExactMtchId = function(){
		$(thisBtn).val('Save Verification for Ligand Mismatch');
		$('#exactmatchid_mode_'+authAssgnGrp).val('undo');
		$(rslvStatusSpanLctr).hide();
		$(attnReqdSpanLctr).show();
		
		$(glblBatchRsltsTbl+' tr.c_'+authAssgnGrp+' .resolve_status').each( function() {
			$(this).html('Mismatch(es) Require Attention');
			$(this).addClass('warn');
		});
		
		//numAssgndInGrp = numAssgndInGrp - instAssgnChngCnt;
		//$('#'+authAssgnGrp+'_assgn_cnt').html(numAssgndInGrp);
		
		$(radioInputsLctr).each(function() {
			$(this).removeAttr('disabled');
		});
		
		$(addrssMsmtchOptsFrm).ajaxSubmit({url: ChemCompLiteMod.URL.SAVE_EXCT_MTCH_ID, async: true, clearForm: false,
	        success: function() {
	        	applyRslvStatusHighlight(authAssgnGrp);
	        	var indx = ChemCompLiteMod.ligIdsRslvd.indexOf(authAssgnGrp);
	        	if( indx >= 0 ){
	            	ChemCompLiteMod.ligIdsRslvd.splice(indx,1);
	            }
				trackRslvdLigIds();
	        	//alert('UNDO: SUCCESS VERIFICATION MESSAGE HERE');
	        }
	    });
	};
	
	
	if( request.indexOf('Save') >= 0 ){
		doSvExactMtchId();
	}
	else{
		doUndoExactMtchId();
	}
	
});

$(document).on("click","input.addrss_msmtch.use_orig_proposed_id", function(){
	//alert('Captured click event');
	var checked = $(this).prop("checked");
	var name = $(this).attr('name');
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	//alert("checked is: "+checked+" and name is: "+name);
	var ligId = idSplitArr[(idSplitArr.length-1)];
	//alert("ligId is: "+ligId);
	$("#addrss_msmtch_opts_submit_"+ligId).removeAttr('disabled').show();
	$(".dscr_nw_lig_actions.c_"+ligId).hide('slow');
	$(".descr_new_lgnd_submit_"+ligId).hide('slow');
	$("#addrss_msmtch_opts_frm_"+ligId).css('width','75%');
	if( checked ){
		// set value in form input to be sent to server
		$("#origproposedid_"+ligId).val(ligId);
		
		//need to be sure to clear exactmatchid to be safe so that there
		//is no confusion on server-side as to whether originally proposed
		//or an exact match alternate is being specified
		$("#exactmatchid_"+ligId).val("");
	}
});

$(document).on("click","input.addrss_msmtch.use_exact_mtch_id", function(){
	//alert('Captured click event');
	var checked = $(this).prop("checked");
	var name = $(this).attr('name');
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	//alert("checked is: "+checked+" and name is: "+name);
	var exactMatchId = idSplitArr[(idSplitArr.length-1)];
	var ligId = idSplitArr[(idSplitArr.length-2)];
	//alert("ligId is: "+ligId);
	$("#addrss_msmtch_opts_submit_"+ligId).removeAttr('disabled').show();
	$(".dscr_nw_lig_actions.c_"+ligId).hide('slow');
	$(".descr_new_lgnd_submit_"+ligId).hide('slow');
	$("#addrss_msmtch_opts_frm_"+ligId).css('width','75%');
	if( checked ){
		// set value in form input to be sent to server
		$("#exactmatchid_"+ligId).val(exactMatchId);
		
		//need to be sure to clear origproposedid to be safe so that there
		//is no confusion on server-side as to whether originally proposed
		//or an exact match alternate is being specified
		$("#origproposedid_"+ligId).val("");
	}
});

$(document).on("click","input.addrss_msmtch.dscr_new_lgnd", function(){
	//alert('Captured click event');
	var checked = $(this).prop("checked");
	var name = $(this).attr('name');
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	//alert("checked is: "+checked+" and name is: "+name);
	var ligId = idSplitArr[(idSplitArr.length-1)];
	//alert("ligId is: "+ligId);
	$("#addrss_msmtch_opts_submit_"+ligId).hide();
	$(".dscr_nw_lig_actions.c_"+ligId).show('slow');
	$(".descr_new_lgnd_submit_"+ligId).show('slow');
	$("#addrss_msmtch_opts_frm_"+ligId).css('width','95%');
	enableDscrLgndCntrls(ligId,'undo');
});

$(document).on("click",".lgnd_type", function(){
	//alert('Captured click event');
	var checked = $(this).prop("checked");
	var name = $(this).attr('name');
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	//alert("checked is: "+checked+" and name is: "+name);
	var ligId = idSplitArr[(idSplitArr.length-1)];
	//alert("ligId is: "+ligId);
	$("#next_data_set_"+ligId).show('slow');
	
	checkMissingLigandTypeField(ligId);
});

/***$(document).on("blur",".dscrptr_str", function(){
	//alert('Captured click event');
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	//alert("checked is: "+checked+" and name is: "+name);
	var ligId = idSplitArr[(idSplitArr.length-1)];
	var validDscrptr = checkForValidDescriptorString(ligId);
	//alert("ligId is: "+ligId);
});***/

function checkMissingAssrtdReqdFields(ccid){
	//var mrvnSktch = eval('document.MSketch_'+ccid);
	//var molDataStr;
	var bMissingReqdField = true;
	$('input.reqd.c_'+ccid+':text').each( function() {
		var value = $(this).val();
		//alert("current value is:"+value);
		if( value != "undefined" && value.length > 1 ){
			bMissingReqdField = false;
		}
	});
	
	var value = $('#file_img_'+ccid).val();
	if( value != "undefined" && value.length > 1 ){
		bMissingReqdField = false;
	}else{
		//if no value currently in file input box then check if any image files already uploaded to server
		if( $('#filesonrecord_img_'+ccid).html().length > 1 ){
			bMissingReqdField = false;
			//DEBUG
			//alert(ccid+" has image files uploaded already");
		}
	}
	
	if( bMissingReqdField ){ //if still missing required field at this point then we have no acceptable data for this fieldset so highlight
		$('#fieldset_reqd_assrtd_'+ccid).css({ 'border-color':'#CD0A0A', 'background-color':'#FEF1EC', 'border-style': 'solid', 'border-width': '1px' });
	}else{
		$('#fieldset_reqd_assrtd_'+ccid).css({ 'border-color':'#f6f6f5', 'background-color': '#FFF', 'border-style': 'groove', 'border-width': '2px' });
	}
	return bMissingReqdField;
}

function checkForUploadedImageFiles(ligid,context){
	var haveFiles = false;
	$('#hlprfrm_auth_assgnd_grp').val(ligid);
	$('#hlprfrm_content_type').val('component-image');
	$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.CHECK_FOR_UPLOADED_FILES, async: true, clearForm: false,
        success: function(jsonObj) {
        	if( jsonObj.filesonrecord == 'true' ){
        		haveFiles = true;
        		var fileList = "";
        		for(var x=0; x < jsonObj.filelist.length; x++){
        			if( x>0 ){
        				fileList += ', ';
        			}
        			fileList += jsonObj.filelist[x];
        		}
        		$('#filesonrecord_img_'+ligid).html("Files already uploaded: "+fileList);
        		$("#file_img_span_"+ligid).hide();
        		if( context == "onupload" ){
        			alert("Please note that an image file has previously been uploaded for this ligand. Only one image file is allowed per ligand.\nIf you continue to upload another file, any prior image files will be superseded by the new file.\nIf you do not wish to replace the previously uploaded file, please press the 'Clear' button to remove the currently selected file.");
        		}
        	}else{
        		$('#filesonrecord_img_'+ligid).html("");
        	}
        	
        	// DEBUG alert( "filesonrecord length for "+ligid+" is: "+ $('#filesonrecord_img_'+ligid).html().length );
        	if( context == "requirementscheck"){
        		checkMissingAssrtdReqdFields(ligid);
        	}
        }
    });
    return haveFiles;
}

function checkCompDefFileUploads(ligid,context){
	var haveFiles = false;
	$('#hlprfrm_auth_assgnd_grp').val(ligid);
	$('#hlprfrm_content_type').val('component-definition');
	$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.CHECK_FOR_UPLOADED_FILES, async: true, clearForm: false,
        success: function(jsonObj) {
        	if( jsonObj.filesonrecord == 'true' ){
        		haveFiles = true;
        		var fileList = "";
        		for(var x=0; x < jsonObj.filelist.length; x++){
        			if( x>0 ){
        				fileList += ', ';
        			}
        			fileList += jsonObj.filelist[x];
        		}
        		$('#filesonrecord_refdict_'+ligid).html("Files already uploaded: "+fileList);
        		$("#file_refdict_span_"+ligid).hide();
        		if( context == "onupload" ){
        			alert("Please note that a component definition file has previously been uploaded for this ligand. Only one definition file is allowed per ligand.\nIf you continue to upload another file, any prior definition files will be superseded by the new file.\nIf you do not wish to replace the previously uploaded file, please press the 'Clear' button to remove the currently selected file.");
        		}
        		
        	}else{
        		$('#filesonrecord_refdict_'+ligid).html("");
        	}
        }
    });
    return haveFiles;
}

$(document).on("click","input.reqd:text", function(){
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	var ligId = idSplitArr[(idSplitArr.length-1)];
	$(".descr_new_lgnd_submit_"+ligId).removeAttr('disabled');
});


$(document).on("blur","input.reqd:text", function(){
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	var ligId = idSplitArr[(idSplitArr.length-1)];
	//$(".descr_new_lgnd_submit_"+ligId).removeAttr('disabled');
	//alert("TESTING. moved away from input.");
	var dscrptrStr = ($('#dscrptr_str_'+ligId).val()).trim();
	var dscrptrType = $('#dscrptr_type_'+ligId).val();
	
	if( dscrptrStr && dscrptrStr.length > 0 ){
		var validDscrptrStr = checkForValidInput(dscrptrStr,dscrptrType,"notify");
	}
	
	checkMissingAssrtdReqdFields(ligId);
	
	
});

$(document).on("change","input.reqd:file", function(){
	var id = $(this).attr('id');
	var ligId = id.split('file_img_')[1];
	
	//alert("TESTING. file input changed.");
	checkForUploadedImageFiles(ligId,"onupload");
	
	var value = $(this).val();
	var arrSplit = value.split(".");
	var fileType = arrSplit[(arrSplit.length - 1)];
	var acceptFileType = false;
	var sAcceptedFileTypes = "";
	var sComma = ", ";
	//alert("current value of file_img is:"+value);
	if( value != "undefined" && value.length > 1 ){
		//alert("filetype is: "+fileType);
		for(var x=0; x < ChemCompLiteMod.accptdImgFileTypes.length; x++){
			//alert("comparing "+fileType.toLowerCase()+" to "+ChemCompLiteMod.accptdImgFileTypes[x]);
			if( x == ChemCompLiteMod.accptdImgFileTypes.length - 1 ){
				sComma = "";
			}
			sAcceptedFileTypes += "'"+ChemCompLiteMod.accptdImgFileTypes[x]+"'"+sComma;
			
			if( fileType.toLowerCase() == ChemCompLiteMod.accptdImgFileTypes[x] ){
				acceptFileType = true;
				break;
			}
		}
		if( acceptFileType ){
			$(".descr_new_lgnd_submit_"+ligId).removeAttr('disabled');
			checkMissingAssrtdReqdFields(ligId);
			$("#clear_file_img_"+ligId).show();
		}else{
			alert("Unsupported file type: '"+fileType+"'. Please provide one of the following: "+sAcceptedFileTypes);
			clearFileUpload(id);
		}
		
	}
	
});


$(document).on("change","input.file_upload.descr_nw_lgnd_input.file_refdict", function(){
	var id = $(this).attr('id');
	var ligId = id.split('file_refdict_')[1];
	
	//alert("TESTING. file input changed.");
	checkCompDefFileUploads(ligId,"onupload");
	
	var value = $(this).val();
	var arrSplit = value.split(".");
	var fileType = arrSplit[(arrSplit.length - 1)];
	var acceptFileType = false;
	var sAcceptedFileTypes = "";
	var sComma = ", ";
	//alert("current value of file_img is:"+value);
	if( value != "undefined" && value.length > 1 ){
		//alert("filetype is: "+fileType);
		for(var x=0; x < ChemCompLiteMod.accptdDefFileTypes.length; x++){
			
			if( x == ChemCompLiteMod.accptdDefFileTypes.length - 1 ){
				sComma = "";
			}
			sAcceptedFileTypes += "'"+ChemCompLiteMod.accptdDefFileTypes[x]+"'"+sComma;
			
			if( fileType.toLowerCase() == ChemCompLiteMod.accptdDefFileTypes[x] ){
				acceptFileType = true;
				break;
			}
		}
		if( acceptFileType ){
			$("#clear_file_refdict_"+ligId).show();
		}else{
			alert("Unsupported file type: '"+fileType+"'. Please provide one of the following: "+sAcceptedFileTypes);
			clearFileUpload(id);
		}
		
	}
	
});



$(document).on("click","input.dscrptr_str", function(){
	var id = $(this).attr('id');
	var idSplitArr = id.split('_');
	var ligId = idSplitArr[(idSplitArr.length-1)];
	var marvinBtnLbl = $('#launch_editor_'+ligId).attr('value');
	if( marvinBtnLbl == 'Hide Editor' ){
		$('#sbmt_choice_'+ligId).show('slow');
	}
});

$(document).on("click","input.alt_ccid.reqd:text", function(){
	var thisBtnId = $(this).attr('id');
	limitChars(thisBtnId, 3);
});

$(document).on("click",".instnc_match_rslts .vizcmp_chck_bx", function(){
	//alert('Captured click event');
	var checked = $(this).prop("checked");
	var refid = $(this).attr('value');
	var instid = $(this).attr('name');
	toggleChemCompDisplay(instid,refid,ChemCompLiteMod.SNGL_INSTNC,checked);
});

$(document).on("click",".single_instance .threeD_chck_bx", function(){
	//alert('Captured click event');
	var checked = this.checked;
	var instid = $(this).attr('name');
	var ulElemLocator = ' #instance_data_' + instid;
	var threeDdivElemLocator = ulElemLocator + ' div.threeDviz';
	var expThreeDdivId = 'threeD_'+instid;
	var refThreeDdivId = 'threeD_'+instid+'_ref';
	var threeDdivId;
	var jmolHtmlUrl;
	var refid;
	var authAssgndGrp;
	var loadFilePath;
	if( checked ){
		var uniqeId = getUniqueIdForJsmol(instid);
		//invoke jsmol for experimental data
		if( !( $('#e'+uniqeId+'_appletinfotablediv').length ) ){
			authAssgndGrp = $('#'+expThreeDdivId).attr('name');
			loadFilePath = CC_LITE_SESSION_DATA.servicePathPrefix + ChemCompLiteMod.URL.GET_REPORT_FILE + '?identifier=' + CC_LITE_SESSION_DATA.depId + '&source=author&ligid=' + instid + '&file=' + authAssgndGrp + '_model.cif';
			loadFileJsmol("e"+uniqeId,expThreeDdivId,loadFilePath,"default");
			$('#e'+uniqeId+"_appletinfotablediv").css({'padding-left':'0px', 'border-style':'none'});
			$('#e'+uniqeId+"_appletdiv").css({'padding-left':'0px', 'border-style':'none'});
		}
		//invoke jsmol for dictionary reference
		if( !($('#r'+uniqeId+'_appletinfotablediv').length ) ) {
			if( $('#'+refThreeDdivId).length ){
				refCcId = $('#'+refThreeDdivId).attr('name');
				loadFilePath = CC_LITE_SESSION_DATA.servicePathPrefix + ChemCompLiteMod.URL.GET_REPORT_FILE + '?identifier=' + CC_LITE_SESSION_DATA.depId + '&source=ccd&ligid=' + refCcId + '&file=' + refCcId + '_ideal.cif';
				loadFileJsmol('r'+uniqeId,refThreeDdivId,loadFilePath,"default");
				$('#r'+uniqeId+'_appletinfotablediv').css({'padding-left':'0px', 'border-style':'none'});
				$('#r'+uniqeId+'_appletdiv').css({'padding-left':'0px', 'border-style':'none'});
			}
		}
		$(threeDdivElemLocator).css('display', 'block');
	}
	else{
		$(threeDdivElemLocator).css('display', 'none');
	}
	//$(threeDdivElemLocator).css('display', checked ? 'block' : 'none');
});

$(document).on("click",".single_instance .twoD_chck_bx", function(){
	var checked = this.checked;
	var instid = $(this).attr('name');
	var ulElemLocator = ' #instance_data_' + instid;
	var twoDdivElemLocator = ulElemLocator + ' div.twoDviz';
	$(twoDdivElemLocator).css('display', checked ? 'block' : 'none');
});

$(document).on("click",".inneraccordion .head", function(){	
	var ele = $(this).find('span:first');
	//alert('Captured click');
	ele.toggleClass('ui-icon-circle-arrow-s ui-icon-circle-arrow-e');
	$(this).next().toggle('slow');
	applyBeautyTips();
	return false;
});

$(document).on("click",".launch_editor", function(){	
	//chem_diagram_
	var $thisBtn = $(this);
	var cmd = $thisBtn.val();
	var id = $thisBtn.attr('id');
	var ligid = (id.split('_'))[2];
	var mrvnSktchHtmlUrl = CC_LITE_SESSION_DATA.sessPathPrefix + '/' + ligid +'_mrvnsktch.html';
	checkMissingAssrtdReqdFields(ligid);
	if( cmd == 'Launch Editor'){
		$thisBtn.val('Hide Editor');
		if( $('#marvin_'+ligid).length < 100 ){
			$('#marvin_'+ligid).load(mrvnSktchHtmlUrl, function(){
				//alert("dynamically loaded marvin sketch applet into page.");
			});
		}
		$('#chem_diagram_'+ligid).show("slow");
		$('.descr_new_lgnd_submit_'+ligid).removeAttr('disabled');
		$('#submission_choice_'+ligid).val('sketch');
		
	}
	else{
		$thisBtn.val('Launch Editor');
		$('#chem_diagram_'+ligid).hide("slow");
	}
	
});

$(document).on("click",".importdscrptr", function(){	
	var id = $(this).attr('id');
	var ligid = (id.split('_'))[1];
	var mrvnSktch = eval('document.MSketch_'+ligid);
	var str = '';
	var dscrptrType = $('#dscrptr_type_'+ligid).val();
	//alert("dscrptrType is: "+dscrptrType);
	
	if( mrvnSktch != null && mrvnSktch != "undefined") {
		str = $('#dscrptr_str_'+ligid).val();
		mrvnSktch.setMol(str, dscrptrType);
		$('#submission_choice_'+ligid).val("sketch");
		$('#sbmt_choice_'+ligid).show('slow');
	} else {
		alert("Cannot import molecule:\n"+
		      "no JavaScript to Java communication in your browser.\n");
	}
	checkMissingAssrtdReqdFields(ligid);
	//alert("Attempting to load SMILES string: "+str);
});



$(document).on("click",".checkuploadedfiles", function(){	
	var $thisBtn = $(this);
	var id = $thisBtn.attr('id');
	var ligid = (id.split('_'))[1];
	var contentType = (id.split('_'))[0];
	$('#hlprfrm_auth_assgnd_grp').val(ligid);
	$('#hlprfrm_content_type').val(contentType);
	
	$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.CHECK_FOR_UPLOADED_FILES, async: true, clearForm: false,
        success: function(jsonObj) {
        	try {
        		//alert(jsonObj.htmlmrkup);
        		//$('#jmol_viewer').show();
        		var contentTypeStr;
        		if( contentType == 'component-definition'){
        			contentTypeStr = 'Component Definition';
        		}else{
        			contentTypeStr = 'Component Image';
        		}
				$('#uploaded_files').html(jsonObj.htmlmrkup).dialog({title: contentTypeStr + " Files Being Submitted", width: 400, height:200, modal: true,
					position: { my: "left bottom", at: "right+20 bottom-15", of: $thisBtn }
				});
				
			} catch(err) {
				alert("error on check for uploaded files.");
				$('.errmsg').html(ChemCompLiteMod.errStyle + 'Error: ' + JSON.stringify(jsonObj) + '<br />\n' +	ChemCompLiteMod.adminContact).show().delay(30000).slideUp(800);
			}
        }
    });
    return false;
});

$(document).on("click",".remove_file", function(){
	var $thisBtn = $(this);
	var ligid = $thisBtn.attr('id');
	var fileName = $thisBtn.attr('name');
	$('#hlprfrm_auth_assgnd_grp').val(ligid);
	$('#hlprfrm_file_name').val(fileName);
	
	$('#hlprfrm').ajaxSubmit({url: ChemCompLiteMod.URL.REMOVE_UPLOADED_FILE, async: true, clearForm: false,
        success: function(jsonObj) {
        	try {
        		if( jsonObj.statuscode == "OK" ){
        			alert("File, '"+fileName+"', removed from dataset.");
        			$thisBtn.parent().remove();
        			$('input.file_upload').each( function(){
        				if( $(this).val() == fileName ){
        					var name = $(this).attr("name"); //file_img
        					var id = name+"_span_"+ligid;
        					$("#"+id).html($("#"+id).html());
        					var fileType = name.split("_")[1];
        					$("#filesonrecord_"+fileType+"_"+ligid).html("");
        					$("#file_"+fileType+"_span_"+ligid).show();
                			$("#clear_file_"+fileType+"_"+ligid).hide();
        				}
        			});
        			var fileTypes = ['img','refdict'];
        			for(var n=0; n < fileTypes.length; n++){
	        			if( $("#filesonrecord_"+fileTypes[n]+"_"+ligid).html().length > 1 ){
	        				var filesOnRcrdContent = $("#filesonrecord_"+fileTypes[n]+"_"+ligid).html();
	        				if( filesOnRcrdContent.indexOf(fileName) >= 0 ){
	        					$("#filesonrecord_"+fileTypes[n]+"_"+ligid).html("");
	        					$("#file_"+fileTypes[n]+"_span_"+ligid).show();
	                			$("#clear_file_"+fileTypes[n]+"_"+ligid).hide();
	        				}
	        			}
        			}
        			if( $('#upload_inventory li').size() == 0 ){
						$('#upload_inventory').html('<br /><span>Currently no files on record.</span>');
					}
        			$('#hlprfrm_file_name').val("");
        			checkMissingAssrtdReqdFields(ligid);
        			checkCompDefFileUploads(ligid,"refresh");
        		}
			} catch(err) {
				alert("error on attempt to remove uploaded file.");
				$('.errmsg').html(ChemCompLiteMod.errStyle + 'Error: ' + JSON.stringify(jsonObj) + '<br />\n' +	ChemCompLiteMod.adminContact).show().delay(30000).slideUp(800);
			}
        }
    });
    return false;
});

//function limitChars(textid, limit, infodiv){
function limitChars(textid, limit){
	var text = $('#'+textid).val();
	var textlength = text.length;
	if(textlength > limit){
		alert('Ligand IDs cannot exceed '+limit+' characters!');
		$('#'+textid).val(text.substr(0,limit));
		return false;
	}
	else{
		//$('#' + infodiv).html('You have '+ (limit - textlength) +' characters left.');
		return true;
	}
}
//////////////////////END: EVENT HANDLERS - Instance Browser View //////////////////////////////////////////////////////