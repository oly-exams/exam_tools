async function merge(docs, progress=false, start=0) {
    const mergedPdf = await PDFLib.PDFDocument.create();
    var query = $(".single-doc", docs);
    var button = $('.combine-all', docs);
    const text = button.html();
    const spinner = '<i class="fa fa-spin fa-spinner"></i>'
    if(progress){
      button.html(spinner+" Progress 0/"+query.length);
    }
    for(var i = 0; i < query.length; i++) {
      const elem = query[i];
      var bytes1 = await fetch(elem["href"]).then(res => res.arrayBuffer());
      const pdf1 = await PDFLib.PDFDocument.load(bytes1);
      // remove the coversheet [0,1,2...] -> [1,2...]
      const copiedPages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices().splice(start));
      copiedPages.forEach((page) => mergedPdf.addPage(page));
      if(progress){
        button.html(spinner+" Progress "+(i+1)+"/"+query.length);
      };
    };
    if(progress){
      button.html(spinner+" saving...");
    };
    const pdfDataUri = await mergedPdf.saveAsBase64({ dataUri: true });
    if(progress){
      button.html(text);
    };
    button.attr("href", pdfDataUri);
    $('.combine-all i', docs).addClass("fa-file-pdf-o").removeClass("fa-spinner fa-spin");
}

function merge_on_click(event, progress=false, start=0) {
    var button = $(event.target);
    $("i",button).removeClass("fa-plus-square-o").addClass("fa-spin fa-spinner");
    const docs=button.closest(".student-docs");
    merge(docs, progress=progress, start=start);
    button.off("click");
};

function merge_on_click_remove_cover(event, progress=true) {
  merge_on_click(event, progress=progress, start=1);
}