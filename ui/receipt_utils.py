import textwrap

def format_receipt_text(sale_id, date, seller, items, total, montant_recu=None, mode_paiement=None, monnaie_rendue=None):
    """
    Génère un ticket de caisse au format texte professionnel (80mm width approx ~42-48 chars).
    """
    WIDTH = 48  # Largeur standard ticket
    lines = []
    
    # 1. Header Centré
    lines.append("=" * WIDTH)
    lines.append("SUPERETTE DU QUARTIER".center(WIDTH))
    lines.append("Avenue De la République".center(WIDTH))
    lines.append("Togo 2000".center(WIDTH))
    lines.append("Tel: 00 01 02 03 ".center(WIDTH))
    lines.append("-" * WIDTH)
    
    # 2. Infos Vente
    lines.append(f"Ticket : #{sale_id}".ljust(WIDTH // 2) + f"{date.strftime('%d/%m/%Y %H:%M')}".rjust(WIDTH // 2))
    lines.append(f"Vendeur : {seller}")
    lines.append("-" * WIDTH)
    
    # 3. Articles Header
    # Format: Nom (24) | Qté (3) | PU (9) | Total (10)
    header = f"{'Article':<22} {'Qté':>3} {'P.U.':>9} {'Total':>10}"
    lines.append(header)
    lines.append("-" * WIDTH)
    
    # 4. Articles List
    # 4. Articles List
    for item in items:
        # Si c'est un dict (RealDictRow)
        if isinstance(item, dict) or (hasattr(item, 'keys') and callable(item.keys)):
            nom = item['nom_produit']
            qte = item['quantite_vendue']
            pu = item.get('prix_unitaire', 0)
            total_line = item.get('total_ligne', qte * pu)
        else: # tuple
            nom, qte, pu, total_line = item
            
        # Tronquer le nom si trop long
        if len(nom) > 22:
            nom = nom[:21] + "."
            
        lines.append(f"{nom:<22} {qte:>3} {pu:>9,.0f} {total_line:>10,.0f}")
        
    lines.append("-" * WIDTH)
    
    # 5. Totaux avec alignement droite
    # 5. Totaux avec alignement droite (Total supprimé à la demande)
    # lines.append(f"TOTAL NET :".ljust(25) + f"{total:,.0f} FCFA".rjust(23))
    
    if montant_recu is not None:
        lines.append("-" * WIDTH)
        mode = mode_paiement if mode_paiement else "ESPECES"
        lines.append(f"Mode de règlement : {mode}")
        lines.append(f"Espèces Reçus :".ljust(25) + f"{montant_recu:,.0f} FCFA".rjust(23))
        
        rendu = monnaie_rendue if monnaie_rendue else 0
        lines.append(f"Rendu Monnaie :".ljust(25) + f"{rendu:,.0f} FCFA".rjust(23))
        
    # 6. Footer
    lines.append("=" * WIDTH)
    lines.append("TVA incluse".center(WIDTH))
    lines.append("MERCI DE VOTRE VISITE !".center(WIDTH))
    lines.append("A BIENTOT".center(WIDTH))
    lines.append("=" * WIDTH)
    
    return "\n".join(lines)
