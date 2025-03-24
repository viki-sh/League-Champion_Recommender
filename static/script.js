function searchChampion() {
  const champName = document.getElementById("championInput").value.trim();
  if (!champName) return alert("Please enter a champion name!");
  window.location.href = `recommend.html?champion=${encodeURIComponent(champName)}`;
}

if (window.location.pathname.includes("recommend.html")) {
  const params = new URLSearchParams(window.location.search);
  const champ = params.get("champion");

  if (champ) {
    fetch(`http://127.0.0.1:5000/recommend?champion=${champ}&top_n=10`)
      .then(res => res.json())
      .then(data => {
        const title = document.getElementById("title");
        const list = document.getElementById("recommendList");
        list.innerHTML = "";

        if (data.error) {
          title.textContent = "Champion not found!";
        } else {
          title.textContent = `Top 10 Champions Similar to ${champ}`;
          data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.champion} (${item.similarity})`;
            list.appendChild(li);
          });
        }
      })
      .catch(() => {
        document.getElementById("title").textContent = "Error fetching recommendations!";
      });
  }
}
