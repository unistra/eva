(function(jsGrid) {

    jsGrid.locales.fr = {
        grid: {
            noDataContent: "Acune donnée",
            deleteConfirm: "Voulez vous vraiment supprimer cette épreuve ?",
            pagerFormat: "Pages: {first} {prev} {pages} {next} {last} &nbsp;&nbsp; {pageIndex} de {pageCount}",
            pagePrevText: "<",
            pageNextText: ">",
            pageFirstText: "<<",
            pageLastText: ">>",
            loadMessage: "Chargement en cours...",
            invalidMessage: "Des données incorrectes sont entrées !"
        },

        loadIndicator: {
            message: "Chargement en cours..."
        },

        fields: {
            control: {
                searchModeButtonTooltip: "Recherche",
                insertModeButtonTooltip: "Ajouter une entrée",
                editButtonTooltip: "Changer",
                deleteButtonTooltip: "Effacer",
                searchButtonTooltip: "Trouve",
                clearFilterButtonTooltip: "Effacer",
                insertButtonTooltip: "Ajouter",
                updateButtonTooltip: "Sauvegarder",
                cancelEditButtonTooltip: "Annuler"
            }
        },

        validators: {
            required: { message: "Champ requis" },
            rangeLength: { message: "Longueur de la valeur du champ est hors de la plage définie" },
            minLength: { message: "La valeur du champ est trop court" },
            maxLength: { message: "La valeur du champ est trop long" },
            pattern: { message: "La valeur du champ ne correspond pas à la configuration définie" },
            range: { message: "La valeur du champ est hors de la plage définie" },
            min: { message: "La valeur du champ est trop petit" },
            max: { message: "La valeur du champ est trop grande" }
        }
    };

}(jsGrid, jQuery));

