function searchChampion() {
    const champName = document.getElementById("championInput").value.trim();
    if (!champName) return alert("Please enter a champion name!");
    window.location.href = `recommend.html?champion=${encodeURIComponent(champName)}`;
  }
  
  if (window.location.pathname.includes("recommend.html")) { //checks if url contains recommend.html
    const params = new URLSearchParams(window.location.search); 
    const champ = params.get("champion"); //gets the name of the champion from ?champion = Ahri part of url 
    
    if (champ) { //if champ in url 
    
      fetch(`http://127.0.0.1:5000/recommend?champion=${champ}&top_n=10`) //sends a GET request to {http://127.0.0.1:5000/recommend?champion=${champ}&top_n=10}, which calls recommend() in app.py
        .then(res => res.json()) // gets the JSON response and makes it into a js object
        .then(data => { //gets the title and recommendList from the page
          const title = document.getElementById("title");
          const list = document.getElementById("recommendList"); 
  
          if (data.error) {
            title.textContent = "Champion not found!";
          } else {
            title.textContent = `Top 10 Champions Similar to ${champ}`; // makes a title for the champ
            data.forEach(item => {
              const li = document.createElement("li");
              li.textContent = `${item.champion} (${item.similarity})`;
              list.appendChild(li);
            }); //for each result, adds to html list
          }
        })
        .catch(() => {
          document.getElementById("title").textContent = "Error fetching recommendations!";
        });
    }
  }
   