local proto_telemetry = Proto.new("forza", "Forza Telemetry")

local field_IsRaceOn = ProtoField.int8("forza.IsRaceOn", "IsRaceOn", base.DEC)
local field_TimestampMS = ProtoField.uint32("forza.TimestampMS", "TimestampMS", base.HEX_DEC)
-- rpm
local field_EngineMaxRpm = ProtoField.float("forza.EngineMaxRpm", "EngineMaxRpm", base.DEC)
local field_EngineIdleRpm = ProtoField.float("forza.EngineIdleRpm", "EngineIdleRpm", base.DEC)
local field_CurrentEngineRpm = ProtoField.float("forza.CurrentEngineRpm", "CurrentEngineRpm", base.DEC)
-- acceleration
local field_AccelerationX = ProtoField.float("forza.AccelerationX", "AccelerationX", base.DEC)
local field_AccelerationY = ProtoField.float("forza.AccelerationY", "AccelerationY", base.DEC)
local field_AccelerationZ = ProtoField.float("forza.AccelerationZ", "AccelerationZ", base.DEC)
-- velocity
local field_VelocityX = ProtoField.float("forza.VelocityX", "VelocityX", base.DEC)
local field_VelocityY = ProtoField.float("forza.VelocityY", "VelocityY", base.DEC)
local field_VelocityZ = ProtoField.float("forza.VelocityZ", "VelocityZ", base.DEC)
-- angular velocity
local field_AngularVelocityX = ProtoField.float("forza.AngularVelocityX", "AngularVelocityX", base.DEC)
local field_AngularVelocityY = ProtoField.float("forza.AngularVelocityY", "AngularVelocityY", base.DEC)
local field_AngularVelocityZ = ProtoField.float("forza.AngularVelocityZ", "AngularVelocityZ", base.DEC)

local field_Yaw = ProtoField.float("forza.Yaw", "Yaw", base.DEC)
local field_Pitch = ProtoField.float("forza.Pitch", "Pitch", base.DEC)
local field_Roll = ProtoField.float("forza.Roll", "Roll", base.DEC)

-- local field_ = ProtoField.float("forza.", "", base.DEC)

-- we attach all fields (normal and generated) to our protocol
proto_telemetry.fields = {
    field_IsRaceOn, field_TimestampMS, field_EngineMaxRpm, field_EngineIdleRpm, field_CurrentEngineRpm, 
    field_AccelerationX, field_AccelerationY, field_AccelerationZ, 
    field_VelocityX, field_VelocityY, field_VelocityZ,
    field_AngularVelocityX, field_AngularVelocityY, field_AngularVelocityZ,
    field_Yaw, field_Pitch, field_Roll
}

function proto_telemetry.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = "Forza Telemetry"

    -- We label the entire UDP payload as being associated with our protocol
    local payload_tree = tree:add( proto_telemetry, buffer() )
    local version_len = 1
    -- `version_buffer` holds the range of bytes
    local offset = 0
    local dataBuffer = buffer(offset, 1)
    payload_tree:add_le(field_IsRaceOn, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_TimestampMS, dataBuffer)
    --
    -- RPM
    --
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_EngineMaxRpm, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_EngineIdleRpm, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_CurrentEngineRpm, dataBuffer)
    --
    -- ACCELERATION
    --
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AccelerationX, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AccelerationY, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AccelerationZ, dataBuffer)
    --
    -- VELOCITY
    --
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_VelocityX, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_VelocityY, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_VelocityZ, dataBuffer)
    --
    -- ANGULAR VELOCITY
    --
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AngularVelocityX, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AngularVelocityY, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_AngularVelocityZ, dataBuffer)
    --
    -- YAW, PITCH, ROLL
    --
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_Yaw, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_Pitch, dataBuffer)
    -- inc
    offset = offset + 4
    dataBuffer = buffer(offset, 4)
    payload_tree:add_le(field_Roll, dataBuffer)
end

udp_table = DissectorTable.get("udp.port")
udp_table:add(5200,proto_telemetry)