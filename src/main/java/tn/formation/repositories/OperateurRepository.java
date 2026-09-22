package tn.formation.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;
import tn.formation.entities.Operateur;
import tn.formation.entities.Produit;




@Repository
public interface OperateurRepository extends CrudRepository<Operateur, Long> {

}
