const searchWrapper = document.querySelector(".search-input");
const inputBox = searchWrapper.querySelector(".input");
const suggBox = searchWrapper.querySelector(".autocom-box");

function getSuggestions (searchTerm) {
    return new Promise(function (resolve, reject) {
        fetch(`/suggest-movies?search=${searchTerm}`)
            .then(function (response) {
                if (response.ok) {
                    return response.json()
                }
                else {
                    reject();
                }
            })
            .then(function (suggestions) {
                resolve(suggestions);
            })
    })
}

inputBox.onkeyup = (e)=>{
    let userData = e.target.value; //user entered data
    let emptyArray = [];
    if(userData){

        getSuggestions(userData)
            .then(function (suggestions) {
                emptyArray = suggestions;

                emptyArray = emptyArray.map((data)=>{
                    // passing return data inside li tag
                    return `<li class="suggest">${data}</li>`;
                });
                searchWrapper.classList.add("active"); //show autocomplete box
                showSuggestions(emptyArray);
                let allList = suggBox.querySelectorAll(".suggest");
                for (let i = 0; i < allList.length; i++) {
                    //adding onclick attribute in all li tag
                    allList[i].setAttribute("onclick", "select(this)");
                }

            })
            .catch(function () {
                throw new Error("Suggestions could not be retrieved.")
            })
    }else{
        searchWrapper.classList.remove("active"); //hide autocomplete box
    }
}
function select(element){
    let selectData = element.textContent;
    inputBox.value = selectData;
    window.location.href = `/show-recommendation/${selectData}`
    searchWrapper.classList.remove("active");
}
function showSuggestions(list){
    let listData;
    if(!list.length){
        userValue = inputBox.value;
        listData = `<li>${userValue}</li>`;
    }else{
      listData = list.join('');
    }
    suggBox.innerHTML = listData;
}
