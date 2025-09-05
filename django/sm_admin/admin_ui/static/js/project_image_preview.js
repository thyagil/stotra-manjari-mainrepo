document.addEventListener("DOMContentLoaded", function () {
    function addPreview(inputSelector, imgId) {
        const input = document.querySelector(inputSelector);
        const preview = document.querySelector(imgId);

        if (input && preview) {
            input.addEventListener("change", function () {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        preview.src = e.target.result;
                        preview.style.display = "block";
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    addPreview("input[name=cover_image]", "#cover-preview");
    addPreview("input[name=banner_image]", "#banner-preview");
});
