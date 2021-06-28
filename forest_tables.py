from pghelp import PGExpressions, PGInterface, Loop
import utils


USER_DATABASE = ROUTING_DATABASE = utils.get_secret("DATABASE_URL")


RoutingPGExpressions = PGExpressions(
    table="routing",
    create_table="CREATE TABLE IF NOT EXISTS {self.table} \
        (id TEXT PRIMARY KEY, \
        destination CHARACTER VARYING(16), \
        expiration_ms BIGINT\
        status CHARACTER VARYING(8));",
    # number management
    intend_to_buy="INSERT INTO {self.table} (id, status) VALUES ($1, 'pending');",
    mark_bought="UPDATE {self.table} SET status='available' WHERE id=$1;",
    set_destination="UPDATE {self.table} SET destination=$2, status='assigned' WHERE id=$1;",
    set_expiration_ms="UPDATE {self.table} SET expiration_ms=$2 WHERE id=$1;",
    sweep_expired_destinations="UPDATE {self.table} SET expiration_ms=NULL, status='available' WHERE expiration_ms IS NOT NULL AND expiration_ms < (extract(epoch from now()) * 1000);",
    delete="DELETE FROM {self.table} WHERE id=$1", # if you want to turn a number into a signal account
    get_available="SELECT id FROM {self.table} WHERE status='available';",
    # routing
    get_destination="SELECT destination FROM {self.table} WHERE id=$1 AND (expiration_ms > extract(epoch from now()) * 1000 OR expiration_ms is NULL);",
    get_id="SELECT id FROM {self.table} WHERE destination=$1;",
)

GroupRoutingPGExpressions = PGExpressions(
    table="group_routing",
    create_table="CREATE TABLE IF NOT EXISTS {self.table} \
        (id SERIAL PRIMARY KEY, their_sms CHARACTER VARYING(16), \
        our_sms CHARACTER VARYING(16), \
        group_id CHARACTER VARYING(64));",
    get_group_id_for_sms_route="SELECT group_id FROM {self.table} \
        WHERE their_sms=$1 AND our_sms=$2;",
    get_sms_route_for_group="SELECT their_sms, our_sms FROM {self.table} \
        WHERE group_id=$1",
    set_sms_route_for_group="INSERT INTO {self.table} \
        (their_sms, our_sms, group_id)\
        VALUES($1, $2, $3) ON CONFLICT DO NOTHING",
    delete_table="DROP TABLE {self.table};",
)

PaymentsPGExpressions = PGExpressions(
    table="payments",
    create_table="CREATE TABLE IF NOT EXISTS {self.table} (transaction_log_id CHARACTER VARYING(16) PRIMARY KEY, \
            account_id CHARACTER VARYING(16), \
            value_pmob BIGINT, \
            finalized_block_index BIGINT, \
            timestamp_ms BIGINT, \
            expiration_ms BIGINT);",
    get_payment="SELECT * FROM {self.table} WHERE value_pmob=$1 AND expiration_ms < (extract(epoch from now())+3600) * 1000;",
    put_payment="INSERT INTO {self.table} (transaction_log_id, account_id, value_pmob, finalized_block_index, timestamp_ms, expiration_ms) \
                                    VALUES($1, $2, $3, $4, extract(epoch from now()) * 1000, (extract(epoch from now())+3600) * 1000) ON CONFLICT DO NOTHING",
)


# class GroupRouting:
#     connection: Optional[asyncpg.connection.Connection] = None

#     @classmethod
#     async def connect(cls) -> GroupRouting:
#         router = cls()
#         router.connection = asyncpg.connect(ROUTING_DATABASE)
#         return router

#     def set_sms_route_for_group(self, their_sms, our_sms, group_id):
#         return self.connection.execute(
#             "INSERT INTO group_routing (their_sms, our_sms, group_id)"
#             "VALUES ($1, $2, $3);",
#             their_sms,
#             our_sms,
#             group_id,
#         )


class RoutingManager(PGInterface):
    def __init__(
        self,
        queries: PGExpressions = RoutingPGExpressions,
        database: str = USER_DATABASE,
        loop: Loop = None,
    ) -> None:
        super().__init__(queries, database, loop)


class GroupRoutingManager(PGInterface):
    def __init__(
        self,
        queries: PGExpressions = GroupRoutingPGExpressions,
        database: str = USER_DATABASE,
        loop: Loop = None,
    ) -> None:
        super().__init__(queries, database, loop)


class PaymentsManager(PGInterface):
    """Abstraction for operations on the `user` table."""

    def __init__(
        self,
        queries: PGExpressions = PaymentsPGExpressions,
        database: str = USER_DATABASE,
        loop: Loop = None,
    ) -> None:
        super().__init__(queries, database, loop)
