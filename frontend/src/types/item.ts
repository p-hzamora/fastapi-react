
export interface Item {
    id: string;
    name: string;
    description?: string;
    price?: number;
  }
  
  export type ItemEndpoints = {
    "GET /items/": {
      response: Item[];
      request: undefined;
    };
    "PUT /items/{item_id}": {
      response: Item;
      request: Omit<Item, "id">;
      params: { item_id: string };
    };
    "POST /items/": {
      response: Item;
      request: Omit<Item, "id">;
    };
    "DELETE /items/{item_id}": {
      response: boolean;
      request: undefined;
      params: { item_id: string };
    };
    "OPTIONS /items/": {
      response: unknown; // Usually returns CORS headers
      request: undefined;
    };
    "PATCH /items/": {
      response: Item[];
      request: Partial<Omit<Item, "id">>[];
    };
    "TRACE /items/{item_id}": {
      response: unknown; // Usually returns debug information
      request: undefined;
      params: { item_id: string };
    };
  };