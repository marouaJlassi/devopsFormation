package tn.formation.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import tn.formation.entities.Stock;

import java.util.List;

@Repository
public interface StockRepository extends JpaRepository<Stock, Long> {













    @Query("SELECT s FROM Stock s where s.qte< s.qteMin")
    List<Stock> retrieveStatusStock();
}
