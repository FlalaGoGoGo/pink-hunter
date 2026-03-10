import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  GetCommand,
  TransactWriteCommand
} from "@aws-sdk/lib-dynamodb";

const dynamo = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const visitorsTable = process.env.VISITORS_TABLE;
const countersTable = process.env.COUNTERS_TABLE;
const siteCounterKey = process.env.SITE_COUNTER_KEY ?? "pinkhunter";
const allowedOrigins = (process.env.ALLOWED_ORIGINS ?? "")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

function resolveAllowOrigin(origin) {
  if (!origin) {
    return allowedOrigins[0] ?? "*";
  }
  if (allowedOrigins.includes("*") || allowedOrigins.includes(origin)) {
    return origin;
  }
  return allowedOrigins[0] ?? "*";
}

function buildHeaders(origin) {
  return {
    "access-control-allow-origin": resolveAllowOrigin(origin),
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type",
    "content-type": "application/json; charset=utf-8"
  };
}

function json(statusCode, body, origin) {
  return {
    statusCode,
    headers: buildHeaders(origin),
    body: JSON.stringify(body)
  };
}

function badRequest(message, origin) {
  return json(400, { error: message }, origin);
}

async function readCounter() {
  const result = await dynamo.send(
    new GetCommand({
      TableName: countersTable,
      Key: { site: siteCounterKey }
    })
  );

  return {
    count: Number(result.Item?.total ?? 0),
    updatedAt: String(result.Item?.updated_at ?? new Date(0).toISOString())
  };
}

function isDuplicateVisitorError(error) {
  if (!error || error.name !== "TransactionCanceledException") {
    return false;
  }

  const reasons = error.CancellationReasons ?? [];
  return reasons.some((reason) => reason?.Code === "ConditionalCheckFailed");
}

async function recordVisitorHit(visitorId, pathname) {
  const updatedAt = new Date().toISOString();
  let incremented = false;

  try {
    await dynamo.send(
      new TransactWriteCommand({
        TransactItems: [
          {
            Put: {
              TableName: visitorsTable,
              Item: {
                visitor_id: visitorId,
                first_seen_at: updatedAt,
                first_pathname: pathname
              },
              ConditionExpression: "attribute_not_exists(visitor_id)"
            }
          },
          {
            Update: {
              TableName: countersTable,
              Key: {
                site: siteCounterKey
              },
              UpdateExpression: "SET total = if_not_exists(total, :zero) + :inc, updated_at = :updatedAt",
              ExpressionAttributeValues: {
                ":zero": 0,
                ":inc": 1,
                ":updatedAt": updatedAt
              }
            }
          }
        ]
      })
    );
    incremented = true;
  } catch (error) {
    if (!isDuplicateVisitorError(error)) {
      throw error;
    }
  }

  const counter = await readCounter();
  return {
    ...counter,
    incremented
  };
}

function parseBody(event) {
  if (!event.body) {
    return {};
  }

  try {
    return JSON.parse(event.body);
  } catch {
    return null;
  }
}

export async function handler(event) {
  const origin = event.headers?.origin ?? event.headers?.Origin ?? "";
  const method = event.requestContext?.http?.method ?? event.httpMethod ?? "GET";
  const path = event.requestContext?.http?.path ?? event.rawPath ?? event.path ?? "/";

  if (!visitorsTable || !countersTable) {
    return json(500, { error: "Missing DynamoDB environment configuration." }, origin);
  }

  if (method === "OPTIONS") {
    return {
      statusCode: 204,
      headers: buildHeaders(origin)
    };
  }

  if (method === "GET" && path.endsWith("/api/v1/visitor-count")) {
    const counter = await readCounter();
    return json(200, counter, origin);
  }

  if (method === "POST" && path.endsWith("/api/v1/visitor-count/hit")) {
    const payload = parseBody(event);
    if (payload == null) {
      return badRequest("Body must be valid JSON.", origin);
    }

    const visitorId = String(payload.visitorId ?? "").trim();
    const pathname = String(payload.pathname ?? "/").trim() || "/";

    if (!visitorId || visitorId.length > 128) {
      return badRequest("visitorId is required and must be 128 characters or fewer.", origin);
    }

    const result = await recordVisitorHit(visitorId, pathname);
    return json(200, result, origin);
  }

  return json(404, { error: "Not found." }, origin);
}
