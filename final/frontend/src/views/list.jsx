import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion
import { Form, InputGroup, Row, Button } from 'react-bootstrap';
import { useAuthStore } from '../store/auth';


const List = () => {
   const [isLoggedIn, user] = useAuthStore((state) => [
      state.isLoggedIn,
      state.user,
  ]);
   const api = useAxios();
   const [ordersList, setOrdersList] = useState([])
   useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await api.get('/get-list-data'); // Replace with your actual endpoint
              const metaData = JSON.parse(response.data)
              console.log(metaData)
              setOrdersList(metaData)
          } catch (error) {
              console.error( error);
          }
      };
  
      fetchData();
  }, []);

  const deleteOrder = async (id) => {
   const deleteData = new FormData(); // Use FormData for multipart file uploads
   deleteData.append('deleteData', JSON.stringify({id})); // Add each image to FormData
   const response = await api.post('/delete-order/', deleteData, {
       headers: {
           'Content-Type': 'multipart/form-data', // Set content type for multipart data
       },
   });
   const metaData = JSON.parse(response.data)
   console.log(metaData)
   setOrdersList(metaData)
  }

  const setNewStatus = async ({pk, value}) => {
   const statusData = new FormData(); // Use FormData for multipart file uploads
   statusData.append('statusData', JSON.stringify({id: pk, value})); // Add each image to FormData
   const response = await api.post('/update-status-order/', statusData, {
       headers: {
           'Content-Type': 'multipart/form-data', // Set content type for multipart data
       },
   });
   const metaData = JSON.parse(response.data)
   setOrdersList(metaData)
  }
   return(
        <div className='orders-list'>
            {ordersList && ordersList.map((order, key) => {
               let orderData = order.fields
               return(<div className='order-child' key={Math.random()}>
                  <div className='order-child-left'>
                  <div className='order-child-title'> {orderData.title} </div>
                  <div className='order-child-cost'> {orderData.cost}$ </div>
                  </div>
                  <div className='order-child-right'>
                  <Form.Group className="col col-sm-12">
                        <Form.Select className="form-control" name="size" value={orderData.status} onChange={(e) => setNewStatus({pk: order.pk, value: e.target.value})}>
                           {
                              ["DONE","SEWED", "CUT","PAINTED","CREATED"].map((o) => <option key={Math.random()} value={o}>{o}</option>)// .map((o) => <option key={Math.random()} value={o.value}>{o.value}</option>)
                           }
                        </Form.Select>
                  </Form.Group> 
                  <a className='btn btn-success' href={`/order?id=${order.pk}`}>LOOKIN</a>
            {user().user_id === orderData.creator &&
                  
                  <button className='btn btn-danger' onClick={() => deleteOrder(order.pk)}>DELETE</button>
            }
                  </div>
               </div>)
            })}
        </div>
   );
};

export default List;