// src/components/ProductsList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ProductsList = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/products/all', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setProducts(response.data.results);
            } catch (error) {
                console.error('Error fetching products:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Products</h1>
            <ul>
                {products.map(product => (
                    <li key={product.id}>
                        <h2>{product.name}</h2>
                        <p>{product.description}</p>
                        <p>Weight: {product.weight}</p>
                        <p>Wholesale Price: {product.wholesale_price}</p>
                        <p>Amount in Goods: {product.amount_in_goods}</p>
                        <p>Legacy Product: {product.legacy_product ? 'Yes' : 'No'}</p>
                        <p>Created At: {new Date(product.created_at).toLocaleString()}</p>
                        <p>Categories:</p>
                        <ul>
                            {product.categories.map(category => (
                                <li key={category.id}>{category.name}</li>
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ProductsList;
