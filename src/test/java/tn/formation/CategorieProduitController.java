package tn.formation;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import tn.formation.controllers.CategorieProduitController;
import tn.formation.entities.CategorieProduit;
import tn.formation.services.ICategorieProduitService;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CategorieProduitControllerTest {

    // Le Controller que nous voulons tester
    @InjectMocks
    private CategorieProduitController controller;

    // Mock du Service
    @Mock
    private ICategorieProduitService categorieProduitService;

    // TEST 1 : Récupérer toutes les catégories
    @Test
    void testGetCategorieProduit() {
        // Arrange
        List<CategorieProduit> categories = new ArrayList<>();

        CategorieProduit cp1 = new CategorieProduit();
        cp1.setIdCategorieProduit(1L);

        CategorieProduit cp2 = new CategorieProduit();
        cp2.setIdCategorieProduit(2L);

        categories.add(cp1);
        categories.add(cp2);

        when(categorieProduitService.retrieveAllCategorieProduits())
                .thenReturn(categories);

        // Act
        List<CategorieProduit> result = controller.getCategorieProduit();

        // Assert
        assertNotNull(result);
        assertEquals(2, result.size());
        verify(categorieProduitService, times(1)).retrieveAllCategorieProduits();
    }

    // TEST 2 : Récupérer une catégorie par ID
    @Test
    void testRetrieveCategorieProduit() {
        // Arrange
        Long id = 1L;

        CategorieProduit cp = new CategorieProduit();
        cp.setIdCategorieProduit(id);

        when(categorieProduitService.retrieveCategorieProduit(id))
                .thenReturn(cp);

        // Act
        CategorieProduit result = controller.retrieveCategorieProduit(id);

        // Assert
        assertNotNull(result);
        assertEquals(id, result.getIdCategorieProduit());
        verify(categorieProduitService, times(1)).retrieveCategorieProduit(id);
    }

    // TEST 3 : Ajouter une catégorie
    @Test
    void testAddCategorieProduit() {
        // Arrange
        CategorieProduit cp = new CategorieProduit();
        cp.setIdCategorieProduit(1L);

        when(categorieProduitService.addCategorieProduit(cp))
                .thenReturn(cp);

        // Act
        CategorieProduit result = controller.addCategorieProduit(cp);

        // Assert
        assertNotNull(result);
        assertEquals(cp, result);
        verify(categorieProduitService, times(1)).addCategorieProduit(cp);
    }

    // TEST 4 : Supprimer une catégorie
    @Test
    void testRemoveCategorieProduit() {
        // Arrange
        Long id = 1L;

        // Act
        controller.removeCategorieProduit(id);

        // Assert
        verify(categorieProduitService, times(1)).deleteCategorieProduit(id);
    }

    // TEST 5 : Modifier une catégorie
    @Test
    void testModifyCategorieProduit() {
        // Arrange
        CategorieProduit cp = new CategorieProduit();
        cp.setIdCategorieProduit(1L);

        when(categorieProduitService.updateCategorieProduit(cp))
                .thenReturn(cp);

        // Act
        CategorieProduit result = controller.modifyCategorieProduit(cp);

        // Assert
        assertNotNull(result);
        assertEquals(cp, result);
        verify(categorieProduitService, times(1)).updateCategorieProduit(cp);
    }
}
