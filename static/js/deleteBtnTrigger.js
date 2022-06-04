const deleteVenueBtn = document.querySelector(".delete-venue-btn");

if (deleteVenueBtn) {
  deleteVenueBtn.addEventListener("click", (e) => {
    e.preventDefault();

    const venueID = e.target.dataset["id"];

    console.log(venueID);

    fetch(`/venues/${venueID}`, {
      method: "DELETE",
    })
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        console.log(data.status);

        if (data.status === true) {
          window.location.replace("/");
        } else {
          alert(
            "Venue can not be deleted at the moment. Please try again later."
          );
        }
      });
  });
}
