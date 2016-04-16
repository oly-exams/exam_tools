/**
 * Copyright (c) 2015-2016, IPhO 2016 - Michele Dolfi.
 */

'use strict';

CKEDITOR.dialog.add( 'mathjax-mathquill', function( editor ) {
	var EditorWrapper = function( iFrame, editor) {
		var mathEditor, preview, doc = iFrame.getFrameDocument(),
			// texValue
			texValue = '',
			// Is the editor loaded and ready to work.
			isInit = false,

			// Function called when MathJax is loaded.
			loadedHandler = CKEDITOR.tools.addFunction( function() {
				mathEditor = doc.getById( 'editor' );

				var height = Math.max( doc.$.body.offsetHeight, doc.$.documentElement.offsetHeight ),
					width = Math.max( mathEditor.$.offsetWidth, doc.$.body.scrollWidth );
				iFrame.setStyles( {
					width: width + 'px',
					height: height + 'px',
					display: 'inline',
					'vertical-align': 'middle'
				} );
				isInit = true;
				doc.getWindow().$.update( texValue );
			} ),
			updateHandler = CKEDITOR.tools.addFunction( function(value) {
				texValue = value;

				var height = Math.max( doc.$.body.offsetHeight, doc.$.documentElement.offsetHeight );
				iFrame.setStyles( {
					height: height + 'px',
				} );

				if (preview) preview(texValue, 'editor');
			} );

		iFrame.on( 'load', load );

		load();

		function load() {
			doc = iFrame.getFrameDocument();

			if ( doc.getById( 'editor' ) )
				return;

			// Because of IE9 bug in a src attribute can not be javascript
			// when you undo (#10930). If you have iFrame with javascript in src
			// and call insertBefore on such element then IE9 will see crash.
			if ( CKEDITOR.env.ie )
				iFrame.removeAttribute( 'src' );

			doc.write( '<!DOCTYPE html>' +
						'<html>' +
						'<head>' +
							'<meta charset="utf-8">' +
							'<script type="text/javascript">' +
								// Get main CKEDITOR form parent.
								'function getCKE() {' +
									'if ( typeof window.parent.CKEDITOR == \'object\' ) {' +
										'return window.parent.CKEDITOR;' +
									'} else {' +
										'return window.parent.parent.CKEDITOR;' +
									'}' +
								'}' +
								// update function
								'var mathEditor;' +
								'function update(value) {' +
									'mathEditor.mathquill("latex", value);' +
								'}' +

							'</script>' +

							// Load libs.
							'<link href="' + ( editor.config.MathQuillCss ) + '" rel="stylesheet">' +
							'<script src="' + ( editor.config.MathQuilljQuery) + '"></script>' +
							'<script src="' + ( editor.config.MathQuillLib ) + '"></script>' +

							'<script type="text/javascript">' +
								'jQuery(function(){' +
									'mathEditor = jQuery("#editor").on("keyup mathquill.toolbarInput", function(){' +
										'getCKE().tools.callFunction(' + updateHandler + ', jQuery(this).mathquill("latex"));' +
									'});' +
									'getCKE().tools.callFunction(' + loadedHandler + ');' +
								'});' +
							'</script>' +
						'</head>' +
						'<body style="padding:0;margin:0;background:transparent;overflow:hidden">' +
							'<span id="editor" class="mathquill-editor" style="border: 1px solid gray;"></span>' +
						'</body>' +
						'</html>' );
		}

		return {
			/**
			 * Sets the TeX value to be displayed in the `iframe` element inside
			 * the editor.
			 *
			 * @param {String} value TeX string.
			 */
			setValue: function( value ) {
				texValue = value;
				if (isInit)
					doc.getWindow().$.update( texValue );
			},
			/**
			 * Gets the TeX value
			 */
			getValue: function( ) {
				return texValue;
			},
			setUpdatePreview: function(fn) {
				preview = fn;
			}
		};
	};

	var preview,
		lang = editor.lang.mathjax;
	var mathquillEditor;
	var simpleTextarea;

	var updatePreview = function (texValue, mode) {
		preview.setValue( '\\(' + texValue + '\\)' );
		if (mode == 'editor') {
			simpleTextarea.setValue(texValue);
		} else if (mode == 'advanced') {
			mathquillEditor.setValue(texValue);
		}
	};

	return {
		title: lang.title,
		minWidth: 350,
		minHeight: 100,
		contents: [
			{
				id: 'editor',
				label: 'Editor mode',
				title: 'Editor mode',
				elements: [
					{
						type: 'html',
						html:
							'<div style="width:100%;text-align:center;">' +
								'<iframe style="border:0;width:0;height:0;font-size:20px" scrolling="no" frameborder="0" allowTransparency="true" src="' + CKEDITOR.plugins.mathjax.fixSrc + '"></iframe>' +
							'</div>',

						onLoad: function() {
							var iFrame = CKEDITOR.document.getById( this.domId ).getChild( 0 );
							mathquillEditor = new EditorWrapper( iFrame, editor );
						},

						setup: function( widget ) {
							mathquillEditor.setValue( CKEDITOR.plugins.mathjax.trim(widget.data.math) );
							mathquillEditor.setUpdatePreview(updatePreview);
						},

						commit: function( widget ) {
							// Add \( and \) to make TeX be parsed by MathJax by default.
							widget.setData( 'math', '\\(' + mathquillEditor.getValue() + '\\)' );
						}
					},
					{
						id: 'documentation',
						type: 'html',
						html:
							'<div style="width:100%;text-align:right;margin:-8px 0 10px">' +
								'<a class="cke_mathjax_doc" href="' + lang.docUrl + '" target="_black" style="cursor:pointer;color:#00B2CE;text-decoration:underline">' +
									lang.docLabel +
								'</a>' +
							'</div>'
					},
					{
						id: 'documentation',
						type: 'html',
						html:
							'<div>' +
								'Preview:' +
							'</div>'
					},
					( !( CKEDITOR.env.ie && CKEDITOR.env.version == 8 ) ) && {
						id: 'preview',
						type: 'html',
						html:
							'<div style="width:100%;text-align:center;">' +
								'<iframe style="border:0;width:0;height:0;font-size:20px" scrolling="no" frameborder="0" allowTransparency="true" src="' + CKEDITOR.plugins.mathjax.fixSrc + '"></iframe>' +
							'</div>',

						onLoad: function() {
							var iFrame = CKEDITOR.document.getById( this.domId ).getChild( 0 );
							preview = new CKEDITOR.plugins.mathjax.frameWrapper( iFrame, editor );
						},

						setup: function( widget ) {
							preview.setValue( widget.data.math );
						}
					}
				]
			},
			{
				id: 'advanced',
				label: 'Advanced mode',
				title: 'Advanced mode',
				elements: [
					{
						id: 'equation',
						type: 'textarea',
						label: lang.dialogInput,

						onLoad: function() {
							var that = this;
							simpleTextarea = that.getInputElement();

							if ( !( CKEDITOR.env.ie && CKEDITOR.env.version == 8 ) ) {
								this.getInputElement().on( 'keyup', function() {
									updatePreview(that.getInputElement().getValue(), 'advanced');
								} );
							}
						},

						setup: function( widget ) {
							// Remove \( and \).
							this.setValue( CKEDITOR.plugins.mathjax.trim( widget.data.math ) );
						},
					},
					{
						id: 'documentation',
						type: 'html',
						html:
							'<div style="width:100%;text-align:right;margin:-8px 0 10px">' +
								'<a class="cke_mathjax_doc" href="' + lang.docUrl + '" target="_black" style="cursor:pointer;color:#00B2CE;text-decoration:underline">' +
									lang.docLabel +
								'</a>' +
							'</div>'
					},
					{
						id: 'documentation',
						type: 'html',
						html:
							'<div>' +
								'Preview:' +
							'</div>'
					},
					( !( CKEDITOR.env.ie && CKEDITOR.env.version == 8 ) ) && {
						id: 'preview',
						type: 'html',
						html:
							'<div style="width:100%;text-align:center;">' +
							'</div>',
					}
				]
			}
		],
		onLoad : function()
		{
			// Act on tab switching
			this.on('selectPage', function (e) {
				var currentPage = e.data.currentPage;
				var destPage = e.data.page;

				var domId_old = this.getContentElement(currentPage, 'preview').domId;
				var iFrame = CKEDITOR.document.getById( domId_old ).getChild( 0 );
				var domId_new = this.getContentElement(destPage, 'preview').domId;

				CKEDITOR.document.getById( domId_new ).$.appendChild( iFrame.$ );
			});
		}
	};
} );
