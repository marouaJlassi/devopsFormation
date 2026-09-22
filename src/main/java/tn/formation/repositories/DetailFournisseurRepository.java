package tn.formation.repositories;


import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.formation.entities.DetailFournisseur;

@Repository
public interface DetailFournisseurRepository extends JpaRepository<DetailFournisseur, Long> {

}
