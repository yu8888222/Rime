-- Shift+字母 追加辅码处理器
-- 在首音节后追加辅码字母，支持多次按键累积追加（最多2个辅码）
-- 光标始终保持在编码末尾，不移动到辅码位置
-- 墨奇双拼每个音节固定2码（声母+韵母），首音节末尾即第2个字符之后

local rime = require "sbxlm.lib"

local this = {}

---@param env Env
function this.init(env)
  env.base_input = nil      -- 插入辅码前的原始输入
  env.fuzhu_chars = ""      -- 已插入的辅码字符（如 "a" 或 "ab"）
  env.confirmed_pos = 0     -- 记录的 confirmed_position
end

---@param key_event KeyEvent
---@param env Env
function this.func(key_event, env)
  -- 只处理按下事件，带 Shift 且无其他修饰键
  if key_event:release() then
    return rime.process_results.kNoop
  end
  if not key_event:shift() then
    return rime.process_results.kNoop
  end
  if key_event:alt() or key_event:ctrl() or key_event:super() or key_event:caps() then
    return rime.process_results.kNoop
  end

  local keycode = key_event.keycode
  -- A-Z
  if keycode < 0x41 or keycode > 0x5a then
    return rime.process_results.kNoop
  end

  local context = env.engine.context
  -- 必须有候选菜单
  if not context:has_menu() then
    return rime.process_results.kNoop
  end

  -- 获取当前可编辑输入（排除已确认部分）
  local confirmed_position = context.composition:toSegmentation():get_confirmed_position()
  local previous_caret_pos = context.caret_pos
  local current_input = context.input:sub(confirmed_position + 1, previous_caret_pos)

  -- 必须至少有2个音节（4码）才能回头补码
  if #current_input < 4 then
    return rime.process_results.kNoop
  end

  -- 计算预期的当前输入（base_input + 已插入辅码）
  local expected_input
  if env.base_input and env.fuzhu_chars ~= "" then
    -- 在首音节后插入辅码：base[1:2] + fuzhu + base[3:]
    expected_input = env.base_input:sub(1, 2) .. env.fuzhu_chars .. env.base_input:sub(3)
  else
    expected_input = env.base_input
  end

  -- 检查状态是否有效：当前输入必须与预期匹配，且 confirmed_position 一致
  if current_input ~= expected_input or confirmed_position ~= env.confirmed_pos then
    -- 状态失效，重新初始化
    env.base_input = current_input
    env.fuzhu_chars = ""
    env.confirmed_pos = confirmed_position
  end

  -- 辅码最多2个，达到后不插入，但光标移到第二个辅码后面
  if #env.fuzhu_chars >= 2 then
    context.caret_pos = confirmed_position + 2 + #env.fuzhu_chars
    return rime.process_results.kAccepted
  end

  -- 在首音节后（位置2 + 已有辅码数）插入新辅码
  local insert_pos = 2 + #env.fuzhu_chars
  context.caret_pos = confirmed_position + insert_pos

  -- 插入辅码字母（小写）
  local ch = string.char(keycode + 32)
  context:push_input(ch)

  -- 更新状态
  env.fuzhu_chars = env.fuzhu_chars .. ch

  -- 光标保持在编码末尾
  context.caret_pos = #context.input

  return rime.process_results.kAccepted
end

return this
