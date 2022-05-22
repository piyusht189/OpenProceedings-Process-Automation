const fs = require('fs');
PDFParser = require("pdf2json");
var parser = require('xml2json');

let pdfParser = new PDFParser();
require('events').EventEmitter.defaultMaxListeners = 1000000;



console.log("---------------- Finding and validating edbt.xml... ----------------");
fs.readFile( 'main_data/proceedings/edbt.xml', function(err, data) {
	if(data){
		var buf = Buffer.from(data);
		buf = buf.toString();
    	buf = buf.replace(/&/g,"&amp;");
		var json = JSON.parse(parser.toJson(buf, {reversible: true}));
		
		
		console.log("---------------- XML format is valid... ----------------");


		let combined_json_papers = [];
		if(json && json.conf && json.conf.track){
			json.conf.track.forEach(e => {
				if(e.paper){
					if(Array.isArray(e.paper)){
					  e.paper.forEach(p_e => {
						combined_json_papers.push(p_e);
					  })
				    }
			    }
			})

			
			
			let meta_data_results = check_metadata(combined_json_papers); // Main key checking happens here

			if(meta_data_results.success){
				fs.writeFile('edbt.json', JSON.stringify(meta_data_results.papers), 'utf8', () => {
					console.log("File edbt.json created!")
				});
				console.log("---------------- Sanity Check Done Succesfully... ----------------");
			}else{
				console.log("------ " + meta_data_results.message + " ------");
			}
	    }else{
		   	console.log("Configuration and Tracks missing...");
		}
		
	}
    if(err){
    	console.log("---------------- Error: ", err, " ----------------");
    }
});



//Checking each file for its size (should be less than 5 MB)
function check_file_size(url){
	if(fs.existsSync(url)){
		var stats = fs.statSync(url);
	    var fileSizeInBytes = stats.size;
	    var fileSizeInMegabytes = fileSizeInBytes / (1024*1024);
	    return fileSizeInMegabytes <= 5 ? true : false;
    }else{
    	return false;
    }
}

//Checking each paper for a4 size ratio.
async function check_file_pages_a4(url){
	if(fs.existsSync(url)){
		pdfParser.loadPDF(url); // ex: ./abc.pdf
		await pdfParser.on("pdfParser_dataReady", pdfData => {
		  let flag = true;
		  width = pdfData.formImage.Width / 4.5; // pdf width
		  pdfData.formImage.Pages.forEach(item => {
		  		height = item.Height / 4.5; // page height
		  		if((height/width).toFixed(4) != 1.4143){
		  			console.log((height/width).toFixed(4))
		  			flag = false;
		  		}
		  });
		  return flag;
		  
		});
   }else{
   	 return false;
   }
}

// Checking if the paper docs are available or not , also checking metadata like author.
function check_metadata(papers){
	console.log("---------------- Checking whole-metadata, File Size & Paper Size if empty or invalid... ----------------");
	let message = "Configuration and Tracks missing...";
	let final_papers_exclude = [];
	let final_papers = JSON.parse(JSON.stringify(papers));
	if(papers){
		let break_loop = false;
		let BreakException = {};
		try {
			  message = "";
			  papers.forEach((e,i) => {
			  			let stop_process = false;
						if(e['author'] && e['title'] && e['path'] 
							&& e['pitch'] && e['poster'] && e['presentation']){
							if(e['author'].length || Object.keys(e['author']).length){
								try {
								  if (!fs.existsSync('main_data/proceedings/' + e['pitch']['$t'])) { // Checking for empty pitch path
								    //Pitch file does not exists
								  	message = "Pitch File (.mp4) does not exist for paper with title: " + e.title['$t']
								  }
								  if (!fs.existsSync('main_data/proceedings/' + e['poster']['$t'])) { // Checking for empty poster path
								    //Poster file does not exists
								  	message = "Poster File (.png) does not exist for paper with title: " + e.title['$t']
								  }
								  if (!fs.existsSync('main_data/proceedings/' + e['path']['$t'])) { // Checking for empty doc path
								    //Paper file does not exists
								  	message = "Paper File (.mp4) does not exist for paper with title: " + e.title['$t']
								  	if(!final_papers_exclude.includes(i)){
								  		final_papers_exclude.push(i);
								  		stop_process = true;
								  	}
								  }
								} catch(err) {
								  console.log(e, message);
								  break_loop = true;
								  throw BreakException;
								}

								if(!stop_process){
								 try {
								  if (!check_file_size('main_data/proceedings/' + e['path']['$t'])) {
								    //Paper file size exceeded
								  	message = "Paper File (.pdf) exceeded 5 MB for paper with title: " + e.title['$t']
								  	if(!final_papers_exclude.includes(i)){
								  		final_papers_exclude.push(i);
								  	}
								  }
								  
								} catch(err) {
								  console.log(e, err);
								  break_loop = true;
								  throw BreakException;
								}

								try {
								  let check_file_pages_a4_result = check_file_pages_a4('main_data/proceedings/' + e['path']['$t']);
								  if (!check_file_pages_a4_result) {
								    //Paper file size exceeded
								  	message = "Paper File (.pdf) does not have A4 Page size for paper with title: " + e.title['$t']
								  	if(!final_papers_exclude.includes(i)){
								  		final_papers_exclude.push(i);
								  	}
								  }
								  
								} catch(err) {
								  console.log(e, err);
								  break_loop = true;
								  throw BreakException;
								}
							  }									
							}else{
								message = "No Auther found for paper with title: " + e.title['$t']
								break_loop = true;
								throw BreakException;
							}
						}else{
							message = "Author, Title, Path, Pitch, Poster or Presentation key not provided for paper index: " + (i+1)
							break_loop = true;
							throw BreakException;
					    }
					})
			} catch (e) {
			  if (e !== BreakException) throw e;
			}
			for (var i = final_papers_exclude.length -1; i >= 0; i--){
                final_papers.splice(final_papers_exclude[i],1);
			}
			return break_loop ? {message: message} : {success: true, papers: final_papers};
		}else{
			return {message: message};
		}
	

}