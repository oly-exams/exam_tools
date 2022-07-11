async function merge(docs) {
    const mergedPdf = await PDFLib.PDFDocument.create();
    var query = $(".single-doc", docs);
    for(var i = 0; i < query.length; i++) {
      const elem = query[i];
      var bytes1 = await fetch(elem["href"]).then(res => res.arrayBuffer());
      const pdf1 = await PDFLib.PDFDocument.load(bytes1);
      // remove the coversheet [0,1,2...] -> [1,2...]
      const copiedPages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices().splice(1));
      copiedPages.forEach((page) => mergedPdf.addPage(page)); 
    };
    const pdfDataUri = await mergedPdf.saveAsBase64({ dataUri: true });
    $('.combine-all', docs).attr("href", pdfDataUri);
    $('.combine-all i', docs).addClass("fa-file-pdf-o").removeClass("fa-spinner fa-spin");
}

function merge_on_click(event) {
    var button = $(event.target);
    $("i",button).removeClass("fa-plus-square-o").addClass("fa-spin fa-spinner");
    const docs=button.closest(".student-docs");
    merge(docs);
    button.off("click");
};