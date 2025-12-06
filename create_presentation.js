const pptxgen = require("pptxgenjs");
const { html2pptx } = require("./html2pptx");

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_16x9";
  pptx.title = "Belt Monitor - System Monitorowania Taśmy";
  pptx.author = "JSW IT Systems Hackathon";
  
  // Add slides
  await html2pptx("presentation/slide1.html", pptx);
  await html2pptx("presentation/slide2.html", pptx);
  await html2pptx("presentation/slide3.html", pptx);
  await html2pptx("presentation/slide4.html", pptx);
  await html2pptx("presentation/slide5.html", pptx);
  await html2pptx("presentation/slide6.html", pptx);
  await html2pptx("presentation/slide7.html", pptx);
  await html2pptx("presentation/slide8.html", pptx);
  
  await pptx.writeFile("Belt_Monitor_Presentation.pptx");
  console.log("Presentation created: Belt_Monitor_Presentation.pptx");
}

createPresentation().catch(console.error);
