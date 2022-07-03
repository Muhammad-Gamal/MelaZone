const btnAnswer = document.getElementById('sav');
var c = 0;
const fetchData = () => {
  // const Q3 = document.getElementById('insure').value;
  const Q5 = document.getElementById('hair_col').value;
  const Q6 = document.getElementById('relatives').value;
  const Q7 = document.getElementById('cancer').value;
  const Q8 = document.getElementById('age__').value;
  const Q9 = document.getElementById('check').value;
  const Q10 = document.getElementById('skin_canc').value;
  const Q11 = document.getElementById('future_risk').value;
  const Q12 = document.getElementById('sun_screen').value;
  const Q13 = document.getElementById('moles').value;
  const Q14 = document.getElementById('tan').value;

  // if (Q3 == 'Yes') {
  //   c += 10;
  // }
  if (Q5 == 'Black') {
    c += 2;
  } else if (Q5 == 'Brown/Blond') {
    c += 5;
  } else if (Q5 == 'Red/Auburn') {
    c += 10;
  }

  if (Q6 == 'Yes') {
    c += 10;
  }
  if (Q7 == 'None') {
    c += 1;
  } else if (Q7 == '1:5') {
    c += 5;
  } else if (Q7 == '6:20') {
    c += 8;
  } else if (Q7 == 'More_than_20') {
    c += 10;
  }

  if (Q8 == 'Less_than_46') {
    c += 5;
  } else if (Q8 == '46:50') {
    c += 4;
  } else if (Q8 == '51:55') {
    c += 3;
  } else if (Q8 == '56:60') {
    c += 2;
  } else if (Q8 == '61:65') {
    c += 1;
  } else if (Q8 == '66_or_older') {
    c += 0;
  }

  if (Q9 == 'Never') {
    c += 1;
  } else if (Q9 == 'Once') {
    c += 5;
  } else if (Q9 == 'Two_or_more') {
    c += 10;
  }

  if (Q10 == 'None') {
    c += 1;
  } else if (Q10 == '1') {
    c += 5;
  } else if (Q10 == '2_or_more') {
    c += 10;
  }

  if (Q11 == 'High_unlikely') {
    c += 1;
  } else if (Q11 == 'Somewhat_unlikely') {
    c += 2;
  } else if (Q11 == 'About_the_same_as_other') {
    c += 3;
  } else if (Q11 == 'Somewhat_more_likely') {
    c += 4;
  } else if (Q11 == 'High_likely') {
    c += 5;
  }

  if (Q12 == 'Never') {
    c += 0;
  } else if (Q12 == 'Some or all time') {
    c += 10;
  }

  if (Q13 == 'No_moles') {
    c += 0;
  } else if (Q13 == 'Few_moles') {
    c += 10;
  } else if (Q13 == 'Some_moles') {
    c += 20;
  } else if (Q13 == 'Many_moles') {
    c += 30;
  }

  if (Q14 == 'Tan_deeply') {
    c += 1;
  } else if (Q14 == 'Tan_moderately') {
    c += 5;
  } else if (Q14 == 'Tan_lightly') {
    c += 8;
  } else if (Q14 == 'Not_Tan') {
    c += 10;
  }

  window.location = `/q_result?result=${c}`;
};
const checkInputs = () => {
  const allInp = document.querySelectorAll('.j');

  let f = false;
  for (let i of allInp) {
    if (i.value == '' || i.value == 'N/A') {
      i.style.borderBottom = '0.1px solid red';
      f = true;
    } else {
      i.style.borderBottom = '0.1px solid gray';
    }
  }
  if (f) {
    return false;
  } else {
    return true;
  }
};
btnAnswer.addEventListener('click', (e) => {
  e.preventDefault();
  checkInputs();
  if (checkInputs() == true) {
    fetchData();
  }
});

// console.log(fetchData());
