/**
 * $Id: plugin.js 766 2011-05-06 15:03:41Z wingedfox $
 * $HeadURL: http://svn.debugger.ru/repos/jslibs/Virtual%20Keyboard/tags/VirtualKeyboard.v3.7.2/plugins/ckeditor/plugin.js $
 *
 * Virtual Keyboard plugin for CKEditor.
 * (c) 2011 Ilya Lebedev <ilya@lebedev.net>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * See http://www.gnu.org/copyleft/lesser.html
 *
 * Do not remove this comment if you want to use script!
 * Не удаляйте данный комментарий, если вы хотите использовать скрипт!
 *
 * @author Ilya Lebedev <ilya@lebedev.net>
 * @version $Rev: 766 $
 * @lastchange $Author: wingedfox $
 */
(function(){var i="Jsvk",I="Jsvk";CKEDITOR.plugins.add(i,{requires:['dialog'],init:function(l){var o=[];if(l.config.jsvk_skin){o.push("vk_skin="+encodeURIComponent(l.config.jsvk_skin));}if(l.config.jsvk_layout){o.push("vk_layout="+encodeURIComponent(l.config.jsvk_layout));}if(o.length){o="?"+o.join("&");}CKEDITOR.scriptLoader.load(CKEDITOR.plugins.get(i).path+"jscripts/vk_iframe.js"+o,function(){});var O=l.addCommand(I,new CKEDITOR.dialogCommand(I));O.modes={wysiwyg:1,source:1};O.canUndo=true;l.ui.addButton(I,{label:i,command:I,icon:this.path+'img/jsvk.gif'});var Q=document.createElement('div');Q.style.display="none";document.body.appendChild(Q);CKEDITOR.dialog.add(I,function(l){var _=l.lang.jsvk;return{title:"",left:0,top:0,minWidth:0,minHeight:0,onShow:function(){var c=(l.container.getElementsByTag("textarea").getItem(0)||l.container.getElementsByTag("iframe").getItem(0)).$;var C=this.parts.contents.getFirst().$;IFrameVirtualKeyboard.show(c,C);},onOk:function(){IFrameVirtualKeyboard.close();l.updateElement();Q.appendChild(this.parts.contents.getFirst().$.lastChild);},onCancel:function(){IFrameVirtualKeyboard.close();l.updateElement();Q.appendChild(this.parts.contents.getFirst().$.lastChild);},contents:[{id:'jsvk',label:'',title:'',expand:false,padding:0,elements:[]}],buttons:[CKEDITOR.dialog.okButton]}});}});})();
