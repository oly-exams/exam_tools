async function recursive_fetch(href){
  // wait for pdf task to be finished
  response = await fetch(href, {redirect: "follow"});
  if (response.headers.get('content-type') != 'application/pdf') {
    await new Promise(resolve => setTimeout(resolve, 5000));
    return recursive_fetch(href);
  }
  else{
    return response;
  }
}

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
      var response = await recursive_fetch(elem["href"]);
      var bytes1 = await response.arrayBuffer();
      const pdf1 = await PDFLib.PDFDocument.load(bytes1);
      // remove the coversheet [0,1,2...] -> [1,2...]
      const copiedPages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices().splice(start));
      copiedPages.forEach((page) => mergedPdf.addPage(page));
      if(progress){
        button.html(spinner+" Progress "+(i+1)+"/"+query.length);
      };
    };
    if(progress){
      button.html(spinner + " saving...");
    };
    const pdfBytes = await mergedPdf.save();
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    const pdfBlobUri = URL.createObjectURL(blob);
    if(progress){
        button.html(text);
    };
    button.attr("href", pdfBlobUri);
    $('.combine-all i', docs).addClass("fa-file-pdf-o").removeClass("fa-spinner fa-spin");
}

function merge_on_click(event, progress=false, start=0) {
    var button = $(event.target);
    $("i",button).removeClass("fa-plus-square-o").addClass("fa-spin fa-spinner");
    const docs=button.closest(".student-docs");
    merge(docs, progress=progress, start=start);
    button.off("click");
};

function merge_on_click_remove_cover(event, progress=false) {
  merge_on_click(event, progress=progress, start=1);
}