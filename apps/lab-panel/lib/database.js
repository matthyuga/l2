'use strict';

const mysql = require('mysql2/promise');

function createDatabase(config) {
  const pool = mysql.createPool(Object.assign({}, config, {
    waitForConnections: true,
    connectionLimit: 6,
    queueLimit: 0,
    decimalNumbers: true,
    charset: 'utf8mb4'
  }));

  return {
    pool: pool,
    async query(sql, params) {
      const result = await pool.execute(sql, params || []);
      return result[0];
    },
    async transaction(work) {
      const connection = await pool.getConnection();
      try {
        await connection.beginTransaction();
        const result = await work(connection);
        await connection.commit();
        return result;
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        connection.release();
      }
    },
    async ping() {
      const rows = await pool.query('SELECT 1 AS ok');
      return rows[0][0].ok === 1;
    }
  };
}

module.exports = { createDatabase };
